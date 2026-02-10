"""Bulk import school data from Apify for major US cities/metro areas."""
import sys
import os
import time
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData
from backend.apify_client import ApifySchoolClient
from config.config import Config

# North Carolina and South Carolina - Complete State Coverage
# Format: (name, north_lat, south_lat, east_lng, west_lng)
# These regions cover the ENTIRE states of NC and SC

NC_SC_REGIONS = [
    # North Carolina - Complete coverage divided into overlapping regions
    # NC bounds: ~33.8°N to 36.6°N, -84.3°W to -75.5°W
    ("NC - Region 1 (Western)", 36.6, 35.2, -80.5, -84.3),
    ("NC - Region 2 (Central West)", 36.4, 34.8, -79.5, -81.5),
    ("NC - Region 3 (Central East)", 36.2, 34.5, -78.0, -80.0),
    ("NC - Region 4 (Eastern)", 36.0, 33.8, -75.5, -78.5),
    ("NC - Region 5 (Charlotte Metro)", 35.5, 34.8, -80.0, -81.2),
    ("NC - Region 6 (Triangle)", 36.2, 35.3, -78.0, -79.5),
    ("NC - Region 7 (Coastal)", 34.8, 33.8, -76.0, -78.0),
    
    # South Carolina - Complete coverage divided into overlapping regions  
    # SC bounds: ~32.0°N to 35.2°N, -83.3°W to -78.5°W
    ("SC - Region 1 (Upstate)", 35.2, 33.5, -80.5, -83.3),
    ("SC - Region 2 (Midlands)", 34.5, 32.8, -79.0, -81.5),
    ("SC - Region 3 (Lowcountry)", 33.5, 32.0, -78.5, -80.5),
    ("SC - Region 4 (Charleston Area)", 33.2, 32.5, -79.0, -80.0),
]

# Keep old metros list for reference (commented out)
# MAJOR_METROS = [...]

def subdivide_region(name, north_lat, south_lat, east_lng, west_lng, rows=2, cols=2):
    """
    Subdivide a large region into smaller sub-regions to get more schools.
    Since Apify returns max 50 schools per query, smaller regions = more total schools.
    
    Args:
        name: Base name for the region
        north_lat, south_lat, east_lng, west_lng: Bounding box
        rows: Number of rows to divide into (default 2)
        cols: Number of columns to divide into (default 2)
    
    Returns:
        List of (name, north, south, east, west) tuples
    """
    sub_regions = []
    lat_step = (north_lat - south_lat) / rows
    lng_step = (east_lng - west_lng) / cols
    
    for row in range(rows):
        for col in range(cols):
            sub_north = north_lat - (row * lat_step)
            sub_south = north_lat - ((row + 1) * lat_step)
            sub_east = west_lng + ((col + 1) * lng_step)
            sub_west = west_lng + (col * lng_step)
            
            sub_name = f"{name} - Sub {row+1}-{col+1}"
            sub_regions.append((sub_name, sub_north, sub_south, sub_east, sub_west))
    
    return sub_regions

def generate_all_sub_regions():
    """Generate all sub-regions by subdividing the main regions."""
    all_regions = []
    
    # Subdivide each main region into 3x3 grid (9 sub-regions each)
    # This will give us 9x more queries and should capture significantly more schools
    # 11 main regions × 9 sub-regions = 99 total regions
    for name, north, south, east, west in NC_SC_REGIONS:
        sub_regions = subdivide_region(name, north, south, east, west, rows=3, cols=3)
        all_regions.extend(sub_regions)
    
    return all_regions

def import_schools_for_metro(name, north_lat, south_lat, east_lng, west_lng):
    """Import all schools for a metro area."""
    print(f"\n{'='*60}")
    print(f"Importing schools for: {name}")
    print(f"Bounds: N={north_lat}, S={south_lat}, E={east_lng}, W={west_lng}")
    print(f"{'='*60}")
    
    try:
        client = ApifySchoolClient()
        schools = client.get_schools_by_bounds(
            north_lat=north_lat,
            south_lat=south_lat,
            east_lng=east_lng,
            west_lng=west_lng,
            min_rating=1,
            include_elementary=True,
            include_middle=True,
            include_high=True,
            include_public=True,
            include_private=False,
            include_charter=True,
            include_unrated=False
        )
        
        print(f"Found {len(schools)} schools")
        
        if not schools:
            print(f"WARNING: No schools found for {name}")
            return 0
        
        # Save to database
        db = SessionLocal()
        added = 0
        updated = 0
        skipped = 0
        
        # Group schools by exact location (same coordinates = same school building)
        # A school building might have multiple levels (e.g., K-12 school)
        location_schools = {}  # key: (lat, lng), value: dict with all levels
        
        for school in schools:
            # Extract data
            school_name = school.get('schoolName', '')
            gs_rating = school.get('gsRating')
            school_levels = school.get('schoolLevels', [])
            lat = school.get('latitude')
            lng = school.get('longitude')
            school_address = school.get('address', '')
            
            if not lat or not lng or not gs_rating:
                skipped += 1
                continue
            
            # Round to 4 decimal places (~36 feet precision) to group same building
            lat_key = round(lat, 4)
            lng_key = round(lng, 4)
            location_key = (lat_key, lng_key)
            
            if location_key not in location_schools:
                location_schools[location_key] = {
                    'lat': lat,
                    'lng': lng,
                    'elementary': None,
                    'middle': None,
                    'high': None,
                    'address': school_address
                }
            
            # Store school by level (keep highest rating if multiple schools at same location)
            for level in school_levels:
                level_str = str(level).lower()
                current = location_schools[location_key].get(level_str)
                
                if not current or gs_rating > current.get('rating', 0):
                    location_schools[location_key][level_str] = {
                        'name': school_name,
                        'rating': gs_rating,
                        'address': school_address
                    }
        
        # Save grouped schools to database
        for (lat_key, lng_key), school_data in location_schools.items():
            # Check if we already have a record at this exact location
            existing = db.query(SchoolData).filter(
                SchoolData.latitude.between(school_data['lat'] - 0.0001, school_data['lat'] + 0.0001),
                SchoolData.longitude.between(school_data['lng'] - 0.0001, school_data['lng'] + 0.0001)
            ).first()
            
            if existing:
                # Update with any new/better ratings
                updated_fields = False
                if school_data.get('elementary') and (not existing.elementary_school_rating or 
                                                       school_data['elementary']['rating'] > existing.elementary_school_rating):
                    existing.elementary_school_name = school_data['elementary']['name']
                    existing.elementary_school_rating = school_data['elementary']['rating']
                    existing.elementary_school_address = school_data['elementary']['address']
                    updated_fields = True
                if school_data.get('middle') and (not existing.middle_school_rating or 
                                                  school_data['middle']['rating'] > existing.middle_school_rating):
                    existing.middle_school_name = school_data['middle']['name']
                    existing.middle_school_rating = school_data['middle']['rating']
                    existing.middle_school_address = school_data['middle']['address']
                    updated_fields = True
                if school_data.get('high') and (not existing.high_school_rating or 
                                               school_data['high']['rating'] > existing.high_school_rating):
                    existing.high_school_name = school_data['high']['name']
                    existing.high_school_rating = school_data['high']['rating']
                    existing.high_school_address = school_data['high']['address']
                    updated_fields = True
                
                # Recalculate blended score
                ratings = []
                if existing.elementary_school_rating:
                    ratings.append(existing.elementary_school_rating)
                if existing.middle_school_rating:
                    ratings.append(existing.middle_school_rating)
                if existing.high_school_rating:
                    ratings.append(existing.high_school_rating)
                existing.blended_school_score = sum(ratings) / len(ratings) if ratings else None
                
                if updated_fields:
                    updated += 1
            else:
                # Create new record
                elem = school_data.get('elementary') or {}
                mid = school_data.get('middle') or {}
                high = school_data.get('high') or {}
                
                # Calculate blended score
                ratings = []
                if elem and elem.get('rating'):
                    ratings.append(elem['rating'])
                if mid and mid.get('rating'):
                    ratings.append(mid['rating'])
                if high and high.get('rating'):
                    ratings.append(high['rating'])
                blended = sum(ratings) / len(ratings) if ratings else None
                
                new_school = SchoolData(
                    latitude=school_data['lat'],
                    longitude=school_data['lng'],
                    elementary_school_name=elem.get('name') if elem else None,
                    elementary_school_rating=elem.get('rating') if elem else None,
                    elementary_school_address=elem.get('address') if elem else None,
                    middle_school_name=mid.get('name') if mid else None,
                    middle_school_rating=mid.get('rating') if mid else None,
                    middle_school_address=mid.get('address') if mid else None,
                    high_school_name=high.get('name') if high else None,
                    high_school_rating=high.get('rating') if high else None,
                    high_school_address=high.get('address') if high else None,
                    blended_school_score=blended
                )
                db.add(new_school)
                added += 1
                
                # Commit in batches for performance
                if (added + updated) % 50 == 0:
                    db.commit()
        
        db.commit()
        db.close()
        
        print(f"Added: {added}, Updated: {updated}, Skipped: {skipped}")
        return added + updated
        
    except Exception as e:
        print(f"ERROR importing {name}: {e}")
        import traceback
        traceback.print_exc()
        return 0

def estimate_cost():
    """Estimate the cost of importing all schools in NC and SC."""
    print("\n" + "=" * 60)
    print("COST ESTIMATE FOR NC & SC SCHOOL IMPORT")
    print("=" * 60)
    
    # Apify pricing: $20 per 1,000 results = $0.02 per school
    cost_per_school = 0.02
    
    # Research-based estimates:
    # NC has ~2,600 public schools (elementary + middle + high)
    # SC has ~1,200 public schools
    # Total: ~3,800 public schools
    # Plus charter schools: ~200 in NC, ~100 in SC
    # Total estimate: ~4,100 schools across both states
    
    # However, Apify returns each school once, so we'll get:
    # - Some schools appear in multiple regions (overlap)
    # - But we deduplicate by location
    # - Estimate: 3,500-4,500 unique schools total
    
    estimated_total_schools_low = 3500
    estimated_total_schools_high = 4500
    estimated_total_schools = 4000  # Middle estimate
    
    estimated_cost_low = estimated_total_schools_low * cost_per_school
    estimated_cost_high = estimated_total_schools_high * cost_per_school
    estimated_cost = estimated_total_schools * cost_per_school
    
    total_regions = len(NC_SC_REGIONS)
    
    print(f"\nRegions to import: {total_regions}")
    print(f"  - NC: 7 regions")
    print(f"  - SC: 4 regions")
    print(f"\nEstimated schools:")
    print(f"  - North Carolina: ~2,600 public schools")
    print(f"  - South Carolina: ~1,200 public schools")
    print(f"  - Total (with charters): ~4,000 schools")
    print(f"\nCost per school: ${cost_per_school:.2f}")
    print(f"\nEstimated total cost:")
    print(f"  - Low estimate ({estimated_total_schools_low} schools): ${estimated_cost_low:.2f}")
    print(f"  - Middle estimate ({estimated_total_schools} schools): ${estimated_cost:.2f}")
    print(f"  - High estimate ({estimated_total_schools_high} schools): ${estimated_cost_high:.2f}")
    print(f"\nNote: Actual cost depends on number of schools found by Apify")
    print(f"      Some schools may appear in multiple regions (overlap)")
    print(f"      Script will deduplicate by location")
    print("=" * 60 + "\n")
    
    return estimated_cost, estimated_total_schools

def main():
    """Import schools for all NC and SC regions."""
    parser = argparse.ArgumentParser(description='Bulk import school data for NC and SC')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--no-subdivide', action='store_true', help='Use original large regions instead of subdivided')
    args = parser.parse_args()
    
    print("Bulk School Data Import - North Carolina & South Carolina")
    print("=" * 60)
    
    # Generate regions (subdivided by default, or original if --no-subdivide)
    if args.no_subdivide:
        regions_to_process = NC_SC_REGIONS
        print("Using ORIGINAL large regions")
        print(f"This will process {len(regions_to_process)} regions")
        print(f"Estimated time: ~20-30 minutes")
    else:
        regions_to_process = generate_all_sub_regions()
        print("Using SUBDIVIDED regions (3x3 grid per main region)")
        print(f"This will process {len(regions_to_process)} sub-regions (9x more than original)")
        print(f"Estimated time: ~90-150 minutes ({len(regions_to_process)} regions × 30-60 seconds)")
    
    print("=" * 60)
    
    # Show cost estimate
    estimated_cost, estimated_schools = estimate_cost()
    
    # Adjust estimate for subdivided regions
    if not args.no_subdivide:
        # With 4x more queries, we should get closer to the full school count
        # But cost per school stays the same
        print(f"\nWith subdivided regions, we expect to get closer to the full ~{estimated_schools} schools")
        print(f"Cost will be based on actual schools found (${estimated_cost:.2f} if we get all {estimated_schools})")
    
    if not args.yes:
        response = input(f"Estimated cost: ${estimated_cost:.2f} for ~{estimated_schools} schools. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Import cancelled.")
            return
    else:
        print(f"Estimated cost: ${estimated_cost:.2f} for ~{estimated_schools} schools. Proceeding automatically...")
    
    if not Config.APIFY_API_TOKEN:
        print("ERROR: APIFY_API_TOKEN not set in .env file")
        return
    
    total_imported = 0
    total_cost = 0.0
    cost_per_school = 0.02
    
    for i, (name, north, south, east, west) in enumerate(regions_to_process, 1):
        print(f"\n[{i}/{len(regions_to_process)}] Processing: {name}")
        count = import_schools_for_metro(name, north, south, east, west)
        total_imported += count
        region_cost = count * cost_per_school
        total_cost += region_cost
        
        print(f"Region cost: ${region_cost:.2f} ({count} schools)")
        print(f"Running total: {total_imported} schools, ${total_cost:.2f}")
        
        # Rate limiting - wait between regions to avoid overwhelming Apify
        if i < len(regions_to_process):
            print(f"\nWaiting 10 seconds before next region...")
            time.sleep(10)
    
    print(f"\n{'='*60}")
    print(f"Import complete!")
    print(f"Total schools imported: {total_imported}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
