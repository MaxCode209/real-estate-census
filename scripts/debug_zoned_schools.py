"""Debug script to test zoned schools lookup for a specific address."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import AttendanceZone
from backend.zone_utils import find_zoned_schools
from sqlalchemy import or_
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

def debug_zoned_schools(address):
    """Debug zoned schools lookup for an address."""
    print("=" * 80)
    print(f"DEBUG: Testing zoned schools for address: {address}")
    print("=" * 80)
    
    # Step 1: Geocode address
    print("\n[STEP 1] Geocoding address...")
    lat, lng = geocode_address(address)
    if not lat or not lng:
        print("ERROR: Could not geocode address")
        return
    
    print(f"  ✓ Geocoded to: lat={lat}, lng={lng}")
    
    # Step 2: Load zones from database
    print("\n[STEP 2] Loading attendance zones from database...")
    db = SessionLocal()
    try:
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).all()
        
        print(f"  ✓ Loaded {len(zones)} total zones")
        
        # Count by state and level
        nc_count = sum(1 for z in zones if z.state == 'NC')
        sc_count = sum(1 for z in zones if z.state == 'SC')
        elem_count = sum(1 for z in zones if z.school_level.lower() == 'elementary')
        mid_count = sum(1 for z in zones if z.school_level.lower() == 'middle')
        high_count = sum(1 for z in zones if z.school_level.lower() == 'high')
        
        print(f"    - NC zones: {nc_count}")
        print(f"    - SC zones: {sc_count}")
        print(f"    - Elementary: {elem_count}")
        print(f"    - Middle: {mid_count}")
        print(f"    - High: {high_count}")
        
        # Step 3: Convert to dict format
        print("\n[STEP 3] Converting zones to dict format...")
        zones_list = [zone.to_dict() for zone in zones]
        print(f"  ✓ Converted {len(zones_list)} zones")
        
        # Step 4: Find zoned schools
        print("\n[STEP 4] Testing point-in-polygon for each school level...")
        
        zoned_elementary = find_zoned_schools(lat, lng, zones_list, 'elementary')
        zoned_middle = find_zoned_schools(lat, lng, zones_list, 'middle')
        zoned_high = find_zoned_schools(lat, lng, zones_list, 'high')
        
        print(f"\n  Elementary school found: {zoned_elementary is not None}")
        if zoned_elementary:
            print(f"    ✓ School: {zoned_elementary.get('school_name')}")
            print(f"    ✓ Level: {zoned_elementary.get('school_level')}")
            print(f"    ✓ State: {zoned_elementary.get('state')}")
            print(f"    ✓ District: {zoned_elementary.get('school_district')}")
        
        print(f"\n  Middle school found: {zoned_middle is not None}")
        if zoned_middle:
            print(f"    ✓ School: {zoned_middle.get('school_name')}")
            print(f"    ✓ Level: {zoned_middle.get('school_level')}")
            print(f"    ✓ State: {zoned_middle.get('state')}")
            print(f"    ✓ District: {zoned_middle.get('school_district')}")
        
        print(f"\n  High school found: {zoned_high is not None}")
        if zoned_high:
            print(f"    ✓ School: {zoned_high.get('school_name')}")
            print(f"    ✓ Level: {zoned_high.get('school_level')}")
            print(f"    ✓ State: {zoned_high.get('state')}")
            print(f"    ✓ District: {zoned_high.get('school_district')}")
        
        # Step 5: Check nearby zones (for debugging)
        print("\n[STEP 5] Checking nearby zones (within 0.1 degrees ≈ 7 miles)...")
        from shapely.geometry import Point
        nearby_zones = []
        for zone in zones_list[:100]:  # Check first 100 for speed
            try:
                boundary = zone.get('zone_boundary')
                if not boundary:
                    continue
                
                import json
                if isinstance(boundary, str):
                    boundary_data = json.loads(boundary)
                else:
                    boundary_data = boundary
                
                if boundary_data.get('type') == 'Feature':
                    geometry = boundary_data.get('geometry')
                elif boundary_data.get('type') == 'FeatureCollection':
                    features = boundary_data.get('features', [])
                    if not features:
                        continue
                    geometry = features[0].get('geometry')
                else:
                    geometry = boundary_data
                
                if not geometry:
                    continue
                
                from shapely.geometry import shape
                polygon = shape(geometry)
                bounds = polygon.bounds  # (minx, miny, maxx, maxy)
                
                # Check if point is within bounding box
                point = Point(lng, lat)
                if bounds[0] <= lng <= bounds[2] and bounds[1] <= lat <= bounds[3]:
                    nearby_zones.append({
                        'name': zone.get('school_name'),
                        'level': zone.get('school_level'),
                        'state': zone.get('state'),
                        'bounds': bounds
                    })
            except Exception as e:
                continue
        
        print(f"  Found {len(nearby_zones)} zones with bounding boxes containing the point")
        if nearby_zones:
            print("  Nearby zones (first 5):")
            for zone in nearby_zones[:5]:
                print(f"    - {zone['name']} ({zone['level']}, {zone['state']})")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if zoned_elementary or zoned_middle or zoned_high:
            print("✓ ZONED SCHOOLS FOUND - Should use zone-based lookup")
            print(f"  - Elementary: {zoned_elementary.get('school_name') if zoned_elementary else 'None'}")
            print(f"  - Middle: {zoned_middle.get('school_name') if zoned_middle else 'None'}")
            print(f"  - High: {zoned_high.get('school_name') if zoned_high else 'None'}")
        else:
            print("✗ NO ZONED SCHOOLS FOUND - Will fall back to distance-based lookup")
            print("  Possible reasons:")
            print("    1. Address is not in any attendance zone")
            print("    2. Point-in-polygon test is failing")
            print("    3. Zones don't cover this area")
            print(f"    4. Found {len(nearby_zones)} zones with bounding boxes containing point")
            print("       (but point-in-polygon test failed - check geometry)")
        print("=" * 80)
        
    finally:
        db.close()

if __name__ == '__main__':
    # Test with the address the user provided
    address = "1010 kenliworth ave charlotte nc"
    debug_zoned_schools(address)
