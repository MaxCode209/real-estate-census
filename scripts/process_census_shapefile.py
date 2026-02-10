"""
Process Census ZCTA shapefile and extract boundaries for your zip codes.
This works with a manually downloaded shapefile from Census Bureau.
100% FREE - no API keys needed.
"""
import sys
import os
import json
from pathlib import Path
import zipfile
import tempfile
import shutil

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("ERROR: geopandas required. Install with: pip install geopandas")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def get_zip_codes_from_database():
    """Get all zip codes from database."""
    db = SessionLocal()
    try:
        records = db.query(CensusData).distinct(CensusData.zip_code).all()
        return [record.zip_code for record in records]
    finally:
        db.close()

def process_shapefile(shapefile_path, zip_codes=None):
    """
    Process Census shapefile and extract boundaries.
    
    Args:
        shapefile_path: Path to .zip or .shp file from Census
        zip_codes: List of zip codes to extract. If None, extracts all.
    """
    if not HAS_GEOPANDAS:
        print("\nERROR: geopandas is required.")
        print("Install with: pip install geopandas")
        return False
    
    print("=" * 70)
    print("Processing Census ZCTA Shapefile")
    print("=" * 70)
    
    shapefile_path = Path(shapefile_path)
    
    # Handle zip file
    if shapefile_path.suffix == '.zip':
        print(f"\nExtracting {shapefile_path.name}...")
        extract_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(shapefile_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find .shp file
            shp_file = None
            for file in Path(extract_dir).glob('*.shp'):
                shp_file = file
                break
            
            if not shp_file:
                print("ERROR: Could not find .shp file in zip")
                return False
            
            shapefile_path = shp_file
        except Exception as e:
            print(f"ERROR extracting zip: {e}")
            return False
    
    # Read shapefile
    print(f"\nReading shapefile: {shapefile_path.name}")
    try:
        gdf = gpd.read_file(str(shapefile_path))
        print(f"Found {len(gdf)} ZCTA boundaries")
        
        # Check column names
        print(f"Columns: {list(gdf.columns)}")
        
        # Find zip code column (could be ZCTA5, ZCTA5CE10, etc.)
        zip_col = None
        for col in ['ZCTA5CE10', 'ZCTA5', 'ZIPCODE', 'ZIP_CODE']:
            if col in gdf.columns:
                zip_col = col
                break
        
        if not zip_col:
            print("ERROR: Could not find zip code column in shapefile")
            print(f"Available columns: {list(gdf.columns)}")
            return False
        
        print(f"Using column: {zip_col}")
        
        # Filter to requested zip codes
        if zip_codes:
            gdf_filtered = gdf[gdf[zip_col].isin(zip_codes)]
            print(f"Filtering to {len(gdf_filtered)} requested zip codes...")
        else:
            gdf_filtered = gdf
            print("Processing all zip codes...")
        
        # Save each as GeoJSON
        saved = 0
        for idx, row in gdf_filtered.iterrows():
            zip_code = str(row[zip_col])
            
            # Create single-feature GeoJSON
            single_gdf = gdf_filtered[[idx]]
            geojson = json.loads(single_gdf.to_json())
            
            # Save
            output_file = BOUNDARIES_DIR / f"{zip_code}.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f)
            
            saved += 1
            if saved % 100 == 0:
                print(f"Saved {saved} boundaries...")
        
        print(f"\n[SUCCESS] Saved {saved} zip code boundaries!")
        print(f"Location: {BOUNDARIES_DIR}/")
        print("\nYour app will now use these actual boundaries!")
        
        # Cleanup
        if 'extract_dir' in locals():
            shutil.rmtree(extract_dir)
        
        return True
        
    except Exception as e:
        print(f"ERROR processing shapefile: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process Census ZCTA shapefile and extract boundaries'
    )
    parser.add_argument(
        'shapefile',
        help='Path to Census shapefile (.zip or .shp)'
    )
    parser.add_argument(
        '--zip-codes',
        nargs='+',
        help='Specific zip codes to extract (default: all from database)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Extract all zip codes from shapefile (not just from database)'
    )
    
    args = parser.parse_args()
    
    if args.all:
        zip_codes = None
    elif args.zip_codes:
        zip_codes = args.zip_codes
    else:
        zip_codes = get_zip_codes_from_database()
        print(f"Found {len(zip_codes)} zip codes in your database")
    
    process_shapefile(args.shapefile, zip_codes)

