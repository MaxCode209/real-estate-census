"""Import missing schools for areas that have attendance zones but no school data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData, AttendanceZone
from backend.apify_client import ApifySchoolClient
from sqlalchemy import func, or_, and_
from config.config import Config

def find_areas_needing_schools():
    """Find geographic areas with zones but few/no schools."""
    db = SessionLocal()
    try:
        # Get unique school names from zones
        zone_schools = db.query(
            AttendanceZone.school_name,
            AttendanceZone.state,
            func.count(AttendanceZone.id).label('zone_count')
        ).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).group_by(
            AttendanceZone.school_name,
            AttendanceZone.state
        ).all()
        
        print(f"Found {len(zone_schools)} unique schools in attendance zones")
        
        # Check which ones are in our database
        missing_count = 0
        found_count = 0
        
        for zone_school_name, state, zone_count in zone_schools[:50]:  # Check first 50
            # Try to find in database
            found = False
            # Check all school level columns
            elem = db.query(SchoolData).filter(
                SchoolData.elementary_school_name.ilike(f'%{zone_school_name}%')
            ).first()
            mid = db.query(SchoolData).filter(
                SchoolData.middle_school_name.ilike(f'%{zone_school_name}%')
            ).first()
            high = db.query(SchoolData).filter(
                SchoolData.high_school_name.ilike(f'%{zone_school_name}%')
            ).first()
            
            if elem or mid or high:
                found_count += 1
            else:
                missing_count += 1
                if missing_count <= 10:
                    print(f"  Missing: {zone_school_name} ({state})")
        
        print(f"\nSample check: {found_count} found, {missing_count} missing (first 50 checked)")
        return missing_count > 0
        
    finally:
        db.close()

def import_schools_for_charlotte():
    """Import schools specifically for Charlotte area (where we're testing)."""
    print("=" * 80)
    print("IMPORTING SCHOOLS FOR CHARLOTTE AREA")
    print("=" * 80)
    
    # Charlotte metro bounds
    charlotte_bounds = {
        'north_lat': 35.4,
        'south_lat': 35.0,
        'east_lng': -80.5,
        'west_lng': -81.2
    }
    
    print(f"\nCharlotte Metro Bounds:")
    print(f"  North: {charlotte_bounds['north_lat']}")
    print(f"  South: {charlotte_bounds['south_lat']}")
    print(f"  East: {charlotte_bounds['east_lng']}")
    print(f"  West: {charlotte_bounds['west_lng']}")
    
    try:
        client = ApifySchoolClient()
        print("\n[STEP 1] Fetching schools from Apify (GreatSchools/Zillow)...")
        print("  This may take 30-60 seconds...")
        
        schools = client.get_schools_by_bounds(
            north_lat=charlotte_bounds['north_lat'],
            south_lat=charlotte_bounds['south_lat'],
            east_lng=charlotte_bounds['east_lng'],
            west_lng=charlotte_bounds['west_lng'],
            min_rating=1,
            include_elementary=True,
            include_middle=True,
            include_high=True,
            include_public=True,
            include_private=False,
            include_charter=True,
            include_unrated=False
        )
        
        print(f"\n[STEP 2] Fetched {len(schools)} schools from Apify")
        
        if not schools:
            print("[ERROR] No schools returned from Apify")
            return
        
        # Process and store schools
        db = SessionLocal()
        try:
            added = 0
            updated = 0
            skipped = 0
            
            print(f"\n[STEP 3] Processing and storing schools...")
            
            for i, school in enumerate(schools, 1):
                if i % 10 == 0:
                    print(f"  Processing: {i}/{len(schools)}...")
                
                try:
                    # Extract school data from Apify response
                    # Apify returns different field names - try multiple
                    school_name = (
                        school.get('name') or 
                        school.get('schoolName') or 
                        school.get('title') or
                        'Unknown'
                    )
                    
                    rating = school.get('rating') or school.get('schoolRating')
                    
                    # Get coordinates
                    lat = school.get('latitude') or school.get('lat') or school.get('y')
                    lng = school.get('longitude') or school.get('lng') or school.get('lon') or school.get('x')
                    
                    if not lat or not lng:
                        skipped += 1
                        continue
                    
                    # Get school level
                    school_levels = school.get('schoolLevels', [])
                    if isinstance(school_levels, str):
                        school_levels = [school_levels]
                    
                    # Find or create SchoolData record
                    # Use coordinates to find existing record
                    existing = db.query(SchoolData).filter(
                        SchoolData.latitude.between(float(lat) - 0.001, float(lat) + 0.001),
                        SchoolData.longitude.between(float(lng) - 0.001, float(lng) + 0.001)
                    ).first()
                    
                    if existing:
                        # Update existing record
                        updated_fields = False
                        
                        # Update by school level
                        if 'elementary' in str(school_levels).lower() and not existing.elementary_school_name:
                            existing.elementary_school_name = school_name
                            existing.elementary_school_rating = float(rating) if rating else None
                            updated_fields = True
                        
                        if 'middle' in str(school_levels).lower() and not existing.middle_school_name:
                            existing.middle_school_name = school_name
                            existing.middle_school_rating = float(rating) if rating else None
                            updated_fields = True
                        
                        if 'high' in str(school_levels).lower() and not existing.high_school_name:
                            existing.high_school_name = school_name
                            existing.high_school_rating = float(rating) if rating else None
                            updated_fields = True
                        
                        if updated_fields:
                            updated += 1
                        else:
                            skipped += 1
                    else:
                        # Create new record
                        new_school = SchoolData(
                            latitude=float(lat),
                            longitude=float(lng),
                            address=None  # Apify may not provide full address
                        )
                        
                        # Set school data by level
                        if 'elementary' in str(school_levels).lower():
                            new_school.elementary_school_name = school_name
                            new_school.elementary_school_rating = float(rating) if rating else None
                        
                        if 'middle' in str(school_levels).lower():
                            new_school.middle_school_name = school_name
                            new_school.middle_school_rating = float(rating) if rating else None
                        
                        if 'high' in str(school_levels).lower():
                            new_school.high_school_name = school_name
                            new_school.high_school_rating = float(rating) if rating else None
                        
                        db.add(new_school)
                        added += 1
                    
                    # Commit every 50 schools
                    if (added + updated) % 50 == 0:
                        db.commit()
                        print(f"  Committed batch: {added} added, {updated} updated")
                
                except Exception as e:
                    skipped += 1
                    if skipped <= 5:
                        print(f"  [ERROR] Skipped school {i}: {e}")
                    continue
            
            # Final commit
            db.commit()
            
            print(f"\n{'='*80}")
            print("IMPORT COMPLETE")
            print(f"{'='*80}")
            print(f"  Total schools fetched: {len(schools)}")
            print(f"  Added: {added} new schools")
            print(f"  Updated: {updated} existing schools")
            print(f"  Skipped: {skipped} schools (missing data)")
            print(f"{'='*80}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 80)
    print("IMPORT MISSING SCHOOLS")
    print("=" * 80)
    
    # Check what we need
    print("\n[STEP 0] Checking database status...")
    find_areas_needing_schools()
    
    # Import for Charlotte (where we're testing)
    print("\n" + "=" * 80)
    import_schools_for_charlotte()
    
    print("\n[NOTE] To import for other areas, modify the bounds in this script")
    print("  or use: python scripts/bulk_import_schools.py")
