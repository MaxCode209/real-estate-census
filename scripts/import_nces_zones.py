"""Import NCES School Attendance Boundary Survey (SABS) data into database."""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.models import AttendanceZone, SchoolData
from sqlalchemy import or_
import requests
from pathlib import Path

# NCES SABS Data URLs
# Note: These are large files (500MB+), so we'll need to download and process them
NCES_SABS_2015_2016_URL = "https://nces.ed.gov/programs/edge/data/SABS_2015_2016.zip"

def download_nces_data(output_dir='data/nces_zones'):
    """Download NCES SABS data (if not already downloaded)."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("NCES School Attendance Boundary Survey (SABS) Import")
    print("=" * 60)
    print("\nThis script will help you import school attendance zone boundaries.")
    print("\nSTEP 1: Download NCES Data")
    print("-" * 60)
    print("NCES SABS data is available at:")
    print("  https://nces.ed.gov/programs/edge/sabs")
    print("\nYou need to:")
    print("  1. Download the 2015-2016 School Level Shapefile (684 MB)")
    print("  2. Extract the ZIP file")
    print("  3. Place shapefiles in: data/nces_zones/")
    print("\nThe shapefiles will be named something like:")
    print("  - sabs_1516_school.shp")
    print("  - sabs_1516_school.dbf")
    print("  - sabs_1516_school.shx")
    print("\nOnce you have the shapefiles, run this script again.")
    print("=" * 60)
    
    # Check if shapefiles exist (including in subdirectories)
    shapefiles = list(output_path.rglob("*.shp"))
    if shapefiles:
        print(f"\nFound shapefile: {shapefiles[0]}")
        return str(shapefiles[0])
    else:
        print("\nNo shapefiles found. Please download from NCES first.")
        return None

def convert_shapefile_to_geojson(shapefile_path, output_geojson_path):
    """
    Convert shapefile to GeoJSON.
    Requires: pip install geopandas fiona
    """
    try:
        import geopandas as gpd
        
        print(f"\nConverting {shapefile_path} to GeoJSON...")
        gdf = gpd.read_file(shapefile_path)
        
        # Filter for NC and SC only
        if 'STATEFP' in gdf.columns:
            # State FIPS codes: 37 = NC, 45 = SC
            gdf = gdf[gdf['STATEFP'].isin(['37', '45'])]
        elif 'STATE' in gdf.columns:
            gdf = gdf[gdf['STATE'].isin(['NC', 'SC'])]
        
        print(f"Found {len(gdf)} zones for NC and SC")
        
        # Convert to GeoJSON
        gdf.to_file(output_geojson_path, driver='GeoJSON')
        print(f"Saved to: {output_geojson_path}")
        
        return output_geojson_path
        
    except ImportError:
        print("\nERROR: geopandas not installed")
        print("Install with: pip install geopandas fiona")
        return None
    except Exception as e:
        print(f"\nERROR converting shapefile: {e}")
        return None

def match_zone_to_school(zone_name, zone_level, db):
    """
    Match a zone to a school in the database.
    Returns SchoolData record if found.
    """
    # Try to match by school name and level
    zone_level_map = {
        'elementary': 'elementary',
        'middle': 'middle',
        'high': 'high',
        'high school': 'high',
        'elementary school': 'elementary',
        'middle school': 'middle'
    }
    
    level = zone_level_map.get(zone_level.lower(), zone_level.lower())
    
    # Search in school_data
    if level == 'elementary':
        school = db.query(SchoolData).filter(
            SchoolData.elementary_school_name.ilike(f'%{zone_name}%')
        ).first()
    elif level == 'middle':
        school = db.query(SchoolData).filter(
            SchoolData.middle_school_name.ilike(f'%{zone_name}%')
        ).first()
    elif level == 'high':
        school = db.query(SchoolData).filter(
            SchoolData.high_school_name.ilike(f'%{zone_name}%')
        ).first()
    else:
        school = None
    
    return school

def import_zones_directly_from_shapefile(shapefile_path):
    """Import zones directly from shapefile (more efficient for large files)."""
    try:
        import geopandas as gpd
        import pandas as pd
    except ImportError:
        print("\nERROR: geopandas not installed")
        print("Install with: pip install geopandas fiona")
        return False
    
    db = SessionLocal()
    
    try:
        print(f"\nReading shapefile: {shapefile_path}")
        print("(This may take a few minutes for large files...)")
        
        # Read shapefile
        gdf = gpd.read_file(shapefile_path)
        print(f"Loaded {len(gdf)} total zones from shapefile")
        
        # Filter for NC and SC only
        # Check available columns
        print(f"\nAvailable columns in shapefile: {list(gdf.columns)[:10]}...")  # Show first 10
        
        # Filter for NC and SC using stAbbrev field
        if 'stAbbrev' in gdf.columns or 'STABBREV' in gdf.columns:
            state_col = 'stAbbrev' if 'stAbbrev' in gdf.columns else 'STABBREV'
            original_count = len(gdf)
            gdf = gdf[gdf[state_col].isin(['NC', 'SC'])]
            print(f"Filtered from {original_count} to {len(gdf)} zones using {state_col}")
        elif 'STATEFP' in gdf.columns:
            # State FIPS codes: 37 = NC, 45 = SC
            original_count = len(gdf)
            gdf = gdf[gdf['STATEFP'].isin(['37', '45', 37, 45])]
            print(f"Filtered from {original_count} to {len(gdf)} zones using STATEFP")
        elif 'STATE' in gdf.columns:
            original_count = len(gdf)
            gdf = gdf[gdf['STATE'].isin(['NC', 'SC'])]
            print(f"Filtered from {original_count} to {len(gdf)} zones using STATE")
        else:
            print("\n[WARNING] Could not find state field.")
            print("Will filter during import based on available state data.")
            # Don't filter here, filter during import
        
        total = len(gdf)
        print(f"Filtered to {total} zones for NC and SC")
        print(f"\nImporting {total} attendance zones...")
        
        imported = 0
        skipped = 0
        matched = 0
        
        from shapely.geometry import mapping
        
        for idx, row in gdf.iterrows():
            # Show progress every 50 zones or every 1%
            if (imported + skipped) % 50 == 0 or (imported + skipped) % max(1, total // 100) == 0:
                processed = imported + skipped
                percent = (processed / total) * 100
                print(f"\rProgress: [{percent:.1f}%] {processed}/{total} zones | Imported: {imported} | Matched: {matched} | Skipped: {skipped}", end="", flush=True)
            
            # Get geometry
            geometry = row.geometry
            if geometry is None:
                skipped += 1
                continue
            
            # Check if geometry is empty
            if hasattr(geometry, 'is_empty') and geometry.is_empty:
                skipped += 1
                continue
            
            # Convert geometry to GeoJSON - use shapely mapping
            try:
                geometry_dict = mapping(geometry)
                # Validate the geometry dict
                if not geometry_dict or 'type' not in geometry_dict:
                    raise ValueError("Invalid geometry dict")
            except Exception as e:
                skipped += 1
                if skipped <= 5:
                    print(f"\nDEBUG: Skipped zone {idx} - geometry conversion error: {e}")
                continue
            
            # Extract school information from properties
            # Based on actual SABS shapefile fields:
            # - schnam = school name
            # - level = school level (1=Elementary, 2=Middle, 3=High, 4=Other)
            # - stAbbrev = state abbreviation (NC, SC, etc.)
            # - leaid = LEA (district) ID
            
            # Use bracket notation for pandas Series - access directly
            school_name = 'Unknown'
            if 'schnam' in row.index:
                val = row['schnam']
                if pd.notna(val):
                    school_name = str(val).strip()
            elif 'SCHNAM' in row.index:
                val = row['SCHNAM']
                if pd.notna(val):
                    school_name = str(val).strip()
            
            # Debug: print first few to verify
            if imported < 3:
                print(f"\nDEBUG: Row {idx} - school_name field value: {school_name}")
            
            # School level mapping: 1=Elementary, 2=Middle, 3=High, 4=Other
            try:
                level_code = row['level'] if 'level' in row.index else (row['LEVEL'] if 'LEVEL' in row.index else None)
            except (KeyError, TypeError):
                level_code = None
            
            # Map numeric codes to text
            level_map = {
                '1': 'elementary',
                '2': 'middle', 
                '3': 'high',
                '4': 'other',
                1: 'elementary',
                2: 'middle',
                3: 'high',
                4: 'other'
            }
            school_level = level_map.get(level_code, str(level_code).lower() if level_code else 'unknown')
            
            # Get state from stAbbrev field
            try:
                state_abbrev = row['stAbbrev'] if 'stAbbrev' in row.index else (row['STABBREV'] if 'STABBREV' in row.index else None)
            except (KeyError, TypeError):
                state_abbrev = None
                
            if state_abbrev and pd.notna(state_abbrev):
                state_abbrev = str(state_abbrev).upper().strip()
                if state_abbrev in ['NC', 'SC']:
                    state = state_abbrev
                else:
                    state = None
            else:
                state = None
            
            # District ID (LEA ID) - store as string
            try:
                district = str(row['leaid']) if 'leaid' in row.index and pd.notna(row['leaid']) else None
            except (KeyError, TypeError):
                district = None
            
            # Create zone record
            # data_year must be 4 characters max, use just the year
            zone = AttendanceZone(
                school_name=str(school_name),
                school_level=str(school_level).lower(),
                school_district=str(district) if district else None,
                state=state,
                zone_boundary=json.dumps(geometry_dict),
                data_year='2015',  # Use just the year (4 chars max)
                source='NCES'
            )
            
            # Try to match to school in database
            matched_school = match_zone_to_school(str(school_name), str(school_level), db)
            if matched_school:
                zone.school_id = matched_school.id
                matched += 1
            
            db.add(zone)
            imported += 1
            
            # Commit in batches of 100
            if imported % 100 == 0:
                db.commit()
        
        # Final commit
        db.commit()
        
        print(f"\rProgress: [100.0%] Complete! {total}/{total} processed.                    ")
        print(f"\n{'='*60}")
        print(f"Import Complete!")
        print(f"  Total processed: {total} zones")
        print(f"  Imported: {imported} zones")
        print(f"  Matched to schools: {matched} zones")
        print(f"  Skipped: {skipped} zones")
        print(f"{'='*60}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\nERROR importing zones: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def import_zones_from_geojson(geojson_path):
    """Import zones from GeoJSON file into database."""
    db = SessionLocal()
    
    try:
        print(f"\nLoading GeoJSON file: {geojson_path}")
        print("(This may take a moment for large files...)")
        
        # Try to load the file
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"\n[ERROR] GeoJSON file appears corrupted at position {e.pos}")
            print("Will process directly from shapefile instead...")
            return None
        
        features = geojson_data.get('features', [])
        print(f"Loaded {len(features)} attendance zones from GeoJSON")
        print(f"\nImporting {len(features)} attendance zones...")
        
        imported = 0
        skipped = 0
        matched = 0
        total = len(features)
        
        print(f"Total zones to import: {total}")
        
        for i, feature in enumerate(features, 1):
            # Show progress every 50 zones or every 1%
            if i % 50 == 0 or i % max(1, total // 100) == 0:
                percent = (i / total) * 100
                print(f"\rProgress: [{percent:.1f}%] {i}/{total} zones | Imported: {imported} | Matched: {matched} | Skipped: {skipped}", end="", flush=True)
            
            properties = feature.get('properties', {})
            geometry = feature.get('geometry')
            
            if not geometry:
                skipped += 1
                continue
            
            # Extract school information from properties
            # NCES field names may vary
            school_name = (
                properties.get('NAME') or 
                properties.get('SCHOOL_NAME') or 
                properties.get('SCHNAME') or
                properties.get('name') or
                'Unknown'
            )
            
            school_level = (
                properties.get('LEVEL') or
                properties.get('SCHOOL_LEVEL') or
                properties.get('LEVEL_') or
                properties.get('level') or
                'unknown'
            )
            
            state_fips = properties.get('STATEFP') or properties.get('STATE_FIPS')
            state = 'NC' if state_fips == '37' else 'SC' if state_fips == '45' else None
            
            district = properties.get('LEA_NAME') or properties.get('DISTRICT') or properties.get('district')
            
            # Create zone record
            zone = AttendanceZone(
                school_name=school_name,
                school_level=school_level.lower(),
                school_district=district,
                state=state,
                zone_boundary=json.dumps(geometry),
                data_year='2015-2016',
                source='NCES'
            )
            
            # Try to match to school in database
            matched_school = match_zone_to_school(school_name, school_level, db)
            if matched_school:
                zone.school_id = matched_school.id
                matched += 1
            
            db.add(zone)
            imported += 1
            
            # Commit in batches of 100
            if imported % 100 == 0:
                db.commit()
        
        # Final commit
        db.commit()
        
        print(f"\rProgress: [100.0%] Complete! {total}/{total} processed.                    ")
        print(f"\n{'='*60}")
        print(f"Import Complete!")
        print(f"  Total processed: {total} zones")
        print(f"  Imported: {imported} zones")
        print(f"  Matched to schools: {matched} zones")
        print(f"  Skipped: {skipped} zones")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"\nERROR importing zones: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    """Main import function."""
    print("NCES School Attendance Zone Import")
    print("=" * 60)
    
    # Step 1: Check for shapefiles
    shapefile_path = download_nces_data()
    
    if not shapefile_path:
        print("\nPlease download NCES SABS data first.")
        print("See instructions above.")
        return
    
    # Step 2: Initialize database
    print("\nInitializing database...")
    init_db()
    
    # Step 3: Import zones directly from shapefile (more efficient)
    print("\nImporting zones directly from shapefile...")
    print("(This avoids large GeoJSON file issues)")
    success = import_zones_directly_from_shapefile(shapefile_path)
    
    if not success:
        # Fallback: Try GeoJSON if it exists
        geojson_path = Path('data/nces_zones/zones_nc_sc.geojson')
        if geojson_path.exists():
            print("\nFalling back to GeoJSON import...")
            import_zones_from_geojson(str(geojson_path))
        else:
            print("\n[ERROR] Could not import zones. Please check the error messages above.")
    
    print("\nDone! Attendance zones are now available for true school zoning.")

if __name__ == '__main__':
    main()
