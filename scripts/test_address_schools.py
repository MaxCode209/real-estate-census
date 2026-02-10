"""Test school lookup for a specific address to diagnose issues."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config.config import Config
from backend.database import SessionLocal
from backend.models import AttendanceZone, SchoolData
from backend.zone_utils import find_zoned_schools
from sqlalchemy import or_, text

def test_address(address):
    """Test school lookup for an address."""
    print("="*80)
    print(f"TESTING ADDRESS: {address}")
    print("="*80)
    
    # Geocode address
    print("\n[1] Geocoding address...")
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': Config.GOOGLE_MAPS_API_KEY,
        'components': 'country:US'
    }
    response = requests.get(geocode_url, params=params, timeout=10)
    data = response.json()
    
    if data['status'] != 'OK' or not data['results']:
        print(f"ERROR: Geocoding failed: {data.get('status')}")
        return
    
    location = data['results'][0]['geometry']['location']
    lat = location['lat']
    lng = location['lng']
    print(f"  Location: {lat}, {lng}")
    
    # Check attendance zones
    print("\n[2] Checking attendance zones...")
    db = SessionLocal()
    try:
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).all()
        print(f"  Total zones in database: {len(zones)}")
        
        zones_list = [zone.to_dict() for zone in zones]
        
        # Find zoned schools
        zoned_elementary = find_zoned_schools(lat, lng, zones_list, 'elementary')
        zoned_middle = find_zoned_schools(lat, lng, zones_list, 'middle')
        zoned_high = find_zoned_schools(lat, lng, zones_list, 'high')
        
        print(f"\n  Zoned Schools Found:")
        print(f"    Elementary: {zoned_elementary.get('school_name') if zoned_elementary else 'None'}")
        print(f"    Middle: {zoned_middle.get('school_name') if zoned_middle else 'None'}")
        print(f"    High: {zoned_high.get('school_name') if zoned_high else 'None'}")
        
        # Check if schools are in database
        print("\n[3] Checking if schools are in database...")
        
        if zoned_elementary:
            elem_name = zoned_elementary.get('school_name')
            print(f"\n  Looking for: '{elem_name}'")
            # Try multiple matching strategies
            elem_school = db.query(SchoolData).filter(
                SchoolData.elementary_school_name.ilike(f'%{elem_name}%'),
                SchoolData.elementary_school_rating.isnot(None)
            ).first()
            if elem_school:
                print(f"    ✓ Found: {elem_school.elementary_school_name} ({elem_school.elementary_school_rating})")
            else:
                print(f"    ✗ NOT FOUND in database")
                # Check if name exists without rating
                elem_no_rating = db.query(SchoolData).filter(
                    SchoolData.elementary_school_name.ilike(f'%{elem_name}%')
                ).first()
                if elem_no_rating:
                    print(f"    (Found but no rating)")
        
        if zoned_middle:
            mid_name = zoned_middle.get('school_name')
            print(f"\n  Looking for: '{mid_name}'")
            mid_school = db.query(SchoolData).filter(
                SchoolData.middle_school_name.ilike(f'%{mid_name}%'),
                SchoolData.middle_school_rating.isnot(None)
            ).first()
            if mid_school:
                print(f"    ✓ Found: {mid_school.middle_school_name} ({mid_school.middle_school_rating})")
            else:
                print(f"    ✗ NOT FOUND in database")
        
        if zoned_high:
            high_name = zoned_high.get('school_name')
            print(f"\n  Looking for: '{high_name}'")
            high_school = db.query(SchoolData).filter(
                SchoolData.high_school_name.ilike(f'%{high_name}%'),
                SchoolData.high_school_rating.isnot(None)
            ).first()
            if high_school:
                print(f"    ✓ Found: {high_school.high_school_name} ({high_school.high_school_rating})")
            else:
                print(f"    ✗ NOT FOUND in database")
        
        # Check distance-based fallback
        print("\n[4] Checking distance-based fallback (if zones failed)...")
        if not (zoned_elementary and zoned_middle and zoned_high):
            print("  Zones didn't find all schools, checking distance-based...")
            search_radius = 5.0 / 69.0
            
            # Find nearest schools
            elementary_query = text("""
                SELECT elementary_school_name, elementary_school_rating,
                       3959 * acos(
                           cos(radians(:lat)) * cos(radians(latitude)) * 
                           cos(radians(longitude) - radians(:lng)) + 
                           sin(radians(:lat)) * sin(radians(latitude))
                       ) as distance_miles
                FROM school_data
                WHERE elementary_school_rating IS NOT NULL
                  AND latitude BETWEEN :lat_min AND :lat_max
                  AND longitude BETWEEN :lng_min AND :lng_max
                ORDER BY distance_miles
                LIMIT 3
            """)
            
            elem_results = db.execute(elementary_query, {
                'lat': lat, 'lng': lng,
                'lat_min': lat - search_radius, 'lat_max': lat + search_radius,
                'lng_min': lng - search_radius, 'lng_max': lng + search_radius
            }).fetchall()
            
            print(f"\n  Nearest Elementary Schools:")
            for name, rating, dist in elem_results:
                print(f"    - {name} ({rating}) - {dist:.2f} miles away")
            
            # Check for Sedgefield and Alexander Graham
            print(f"\n  Checking for expected schools:")
            sedgefield_elem = db.query(SchoolData).filter(
                SchoolData.elementary_school_name.ilike('%Sedgefield%')
            ).all()
            if sedgefield_elem:
                for school in sedgefield_elem:
                    dist = 3959 * (3.14159/180) * ((lat - school.latitude)**2 + (lng - school.longitude)**2)**0.5
                    print(f"    Sedgefield Elementary: {school.elementary_school_name} - {dist:.2f} miles")
            
            alex_graham = db.query(SchoolData).filter(
                SchoolData.middle_school_name.ilike('%Alexander Graham%')
            ).all()
            if alex_graham:
                for school in alex_graham:
                    dist = 3959 * (3.14159/180) * ((lat - school.latitude)**2 + (lng - school.longitude)**2)**0.5
                    print(f"    Alexander Graham Middle: {school.middle_school_name} - {dist:.2f} miles")
            
            sedgefield_mid = db.query(SchoolData).filter(
                SchoolData.middle_school_name.ilike('%Sedgefield%')
            ).all()
            if sedgefield_mid:
                for school in sedgefield_mid:
                    dist = 3959 * (3.14159/180) * ((lat - school.latitude)**2 + (lng - school.longitude)**2)**0.5
                    print(f"    Sedgefield Middle: {school.middle_school_name} - {dist:.2f} miles")
        
    finally:
        db.close()
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_address("1111 metropolitan ave charlotte nc 28204")
