"""Test script to debug zoned schools logic for specific addresses."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.models import AttendanceZone, SchoolData
from backend.zone_utils import find_zoned_schools
from backend.apify_client import ApifySchoolClient
from sqlalchemy import or_, text
import requests
from config.config import Config

def geocode_address(address):
    """Geocode an address to get lat/lng."""
    try:
        geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': address,
            'key': Config.GOOGLE_MAPS_API_KEY,
            'components': 'country:US'
        }
        
        response = requests.get(geocode_url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding failed: {data.get('error_message', data.get('status'))}")
            return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None

def test_zoned_schools_logic(address):
    """Test the complete zoned schools logic for an address."""
    print("=" * 80)
    print(f"TESTING ZONED SCHOOLS LOGIC")
    print(f"Address: {address}")
    print("=" * 80)
    
    # Step 1: Geocode
    print("\n[STEP 1] Geocoding address...")
    lat, lng = geocode_address(address)
    if not lat or not lng:
        print("ERROR: Could not geocode address")
        return
    print(f"✓ Geocoded to: lat={lat}, lng={lng}")
    
    db = SessionLocal()
    try:
        # Step 2: Try attendance zones
        print("\n[STEP 2] Testing attendance zones (point-in-polygon)...")
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).all()
        
        print(f"  Loaded {len(zones)} zones from database")
        
        zoned_elementary = None
        zoned_middle = None
        zoned_high = None
        
        if zones:
            zones_list = [zone.to_dict() for zone in zones]
            print(f"  Converted to dict format")
            
            print(f"  Testing point-in-polygon for ({lat}, {lng})...")
            zoned_elementary = find_zoned_schools(lat, lng, zones_list, 'elementary')
            zoned_middle = find_zoned_schools(lat, lng, zones_list, 'middle')
            zoned_high = find_zoned_schools(lat, lng, zones_list, 'high')
        
        use_zones = zoned_elementary or zoned_middle or zoned_high
        print(f"\n  Result: {'✓ FOUND ZONED SCHOOLS' if use_zones else '✗ NO ZONED SCHOOLS FOUND'}")
        print(f"    - Elementary: {zoned_elementary.get('school_name') if zoned_elementary else 'None'}")
        print(f"    - Middle: {zoned_middle.get('school_name') if zoned_middle else 'None'}")
        print(f"    - High: {zoned_high.get('school_name') if zoned_high else 'None'}")
        
        # Step 3: If zones failed, try Apify
        if not use_zones:
            print("\n[STEP 3] Attendance zones failed, trying Apify (GreatSchools/Zillow)...")
            print("  NOTE: This may take 30-60 seconds...")
            try:
                apify_client = ApifySchoolClient()
                apify_elementary, apify_middle, apify_high = apify_client.get_schools_by_address(
                    address, lat, lng, radius_miles=2.0
                )
                
                if apify_elementary:
                    elem_name = apify_elementary.get('name') or apify_elementary.get('schoolName') or apify_elementary.get('title', '')
                    if elem_name:
                        zoned_elementary = {'school_name': elem_name}
                        print(f"  ✓ Apify found elementary: {elem_name}")
                
                if apify_middle:
                    mid_name = apify_middle.get('name') or apify_middle.get('schoolName') or apify_middle.get('title', '')
                    if mid_name:
                        zoned_middle = {'school_name': mid_name}
                        print(f"  ✓ Apify found middle: {mid_name}")
                
                if apify_high:
                    high_name = apify_high.get('name') or apify_high.get('schoolName') or apify_high.get('title', '')
                    if high_name:
                        zoned_high = {'school_name': high_name}
                        print(f"  ✓ Apify found high: {high_name}")
                
                if zoned_elementary or zoned_middle or zoned_high:
                    use_zones = True
                    print(f"  ✓ Apify found zoned schools")
                else:
                    print(f"  ✗ Apify did not return any schools")
            except Exception as e:
                print(f"  ✗ Apify failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 4: Match to database for ratings
        print("\n[STEP 4] Matching school names to database for ratings...")
        
        if use_zones:
            elementary_name = zoned_elementary.get('school_name') if zoned_elementary else None
            middle_name = zoned_middle.get('school_name') if zoned_middle else None
            high_name = zoned_high.get('school_name') if zoned_high else None
            
            print(f"  School names to match:")
            print(f"    - Elementary: {elementary_name}")
            print(f"    - Middle: {middle_name}")
            print(f"    - High: {high_name}")
            
            # Match elementary
            if elementary_name:
                elem_school = db.query(SchoolData).filter(
                    or_(
                        SchoolData.elementary_school_name.ilike(f'%{elementary_name}%'),
                        SchoolData.elementary_school_name == elementary_name
                    ),
                    SchoolData.elementary_school_rating.isnot(None)
                ).first()
                if elem_school:
                    print(f"  ✓ Found rating: {elem_school.elementary_school_rating} for {elem_school.elementary_school_name}")
                else:
                    print(f"  ✗ No rating found for '{elementary_name}'")
                    # Show similar names
                    similar = db.query(SchoolData).filter(
                        SchoolData.elementary_school_name.ilike(f'%{elementary_name[:10]}%')
                    ).limit(3).all()
                    if similar:
                        print(f"    Similar names in database:")
                        for s in similar:
                            print(f"      - {s.elementary_school_name}")
            
            # Match middle
            if middle_name:
                mid_school = db.query(SchoolData).filter(
                    or_(
                        SchoolData.middle_school_name.ilike(f'%{middle_name}%'),
                        SchoolData.middle_school_name == middle_name
                    ),
                    SchoolData.middle_school_rating.isnot(None)
                ).first()
                if mid_school:
                    print(f"  ✓ Found rating: {mid_school.middle_school_rating} for {mid_school.middle_school_name}")
                else:
                    print(f"  ✗ No rating found for '{middle_name}'")
            
            # Match high
            if high_name:
                high_school = db.query(SchoolData).filter(
                    or_(
                        SchoolData.high_school_name.ilike(f'%{high_name}%'),
                        SchoolData.high_school_name == high_name
                    ),
                    SchoolData.high_school_rating.isnot(None)
                ).first()
                if high_school:
                    print(f"  ✓ Found rating: {high_school.high_school_rating} for {high_school.high_school_name}")
                else:
                    print(f"  ✗ No rating found for '{high_name}'")
        else:
            print("\n[STEP 4] No zoned schools found - would fall back to distance-based lookup")
            print("  This is the OLD method (what you're currently seeing)")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if use_zones:
            print("✓ ZONED SCHOOLS APPROACH: Should use zoned schools")
            print(f"  - Elementary: {zoned_elementary.get('school_name') if zoned_elementary else 'None'}")
            print(f"  - Middle: {zoned_middle.get('school_name') if zoned_middle else 'None'}")
            print(f"  - High: {zoned_high.get('school_name') if zoned_high else 'None'}")
        else:
            print("✗ FALLBACK: Using distance-based lookup (old method)")
            print("  This means:")
            print("    1. Attendance zones didn't find a match")
            print("    2. Apify didn't work or wasn't called")
            print("    3. System is using nearest schools by distance")
        print("=" * 80)
        
    finally:
        db.close()

if __name__ == '__main__':
    # Test addresses
    test_addresses = [
        "1010 kenliworth ave charlotte nc",
        # Add more test addresses here
    ]
    
    for address in test_addresses:
        test_zoned_schools_logic(address)
        print("\n\n")
