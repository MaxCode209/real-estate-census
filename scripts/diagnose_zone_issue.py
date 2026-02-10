"""Diagnose why zones aren't matching for an address."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import AttendanceZone
from sqlalchemy import or_
from shapely.geometry import Point, shape
import json

def diagnose_zone_issue(lat, lng, address_name="Test Address"):
    """Diagnose why zones aren't matching."""
    print("=" * 80)
    print(f"DIAGNOSING ZONE ISSUE: {address_name}")
    print(f"Coordinates: lat={lat}, lng={lng}")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Load zones
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).all()
        
        print(f"\n[INFO] Loaded {len(zones)} total zones")
        
        point = Point(lng, lat)
        nearby_zones = []
        matching_zones = []
        
        print(f"\n[STEP 1] Checking bounding boxes (fast check)...")
        for zone in zones[:1000]:  # Check first 1000 for speed
            try:
                boundary_str = zone.zone_boundary
                if not boundary_str:
                    continue
                
                boundary_data = json.loads(boundary_str) if isinstance(boundary_str, str) else boundary_str
                geometry = boundary_data
                
                polygon = shape(geometry)
                bounds = polygon.bounds  # (minx, miny, maxx, maxy)
                
                # Check if point is within bounding box
                if bounds[0] <= lng <= bounds[2] and bounds[1] <= lat <= bounds[3]:
                    nearby_zones.append({
                        'name': zone.school_name,
                        'level': zone.school_level,
                        'state': zone.state,
                        'bounds': bounds
                    })
                    
                    # Now test actual point-in-polygon
                    if polygon.contains(point):
                        matching_zones.append({
                            'name': zone.school_name,
                            'level': zone.school_level,
                            'state': zone.state
                        })
            except Exception as e:
                continue
        
        print(f"  Found {len(nearby_zones)} zones with bounding boxes containing the point")
        print(f"  Found {len(matching_zones)} zones with point actually inside polygon")
        
        if nearby_zones:
            print(f"\n  Nearby zones (first 5):")
            for z in nearby_zones[:5]:
                print(f"    - {z['name']} ({z['level']}, {z['state']})")
        
        if matching_zones:
            print(f"\n  [SUCCESS] Matching zones found:")
            for z in matching_zones:
                print(f"    - {z['name']} ({z['level']}, {z['state']})")
        else:
            print(f"\n  [ISSUE] No zones match - point-in-polygon failing")
            print(f"    Possible reasons:")
            print(f"    1. Address is not in any attendance zone")
            print(f"    2. Zone boundaries don't cover this area")
            print(f"    3. Geometry format issue")
            if len(nearby_zones) > 0:
                print(f"    4. {len(nearby_zones)} zones have bounding boxes containing point,")
                print(f"       but point-in-polygon test failed - check geometry")
        
        # Check a sample zone geometry
        if zones:
            print(f"\n[STEP 2] Checking sample zone geometry format...")
            sample_zone = zones[0]
            boundary_str = sample_zone.zone_boundary
            boundary_data = json.loads(boundary_str) if isinstance(boundary_str, str) else boundary_str
            
            print(f"  Sample zone: {sample_zone.school_name}")
            print(f"  Geometry type: {boundary_data.get('type')}")
            print(f"  Has coordinates: {'coordinates' in boundary_data}")
            if 'coordinates' in boundary_data:
                coords = boundary_data['coordinates']
                if isinstance(coords, list) and len(coords) > 0:
                    print(f"  First coordinate: {coords[0][0] if isinstance(coords[0], list) else 'N/A'}")
        
    finally:
        db.close()

if __name__ == '__main__':
    # Test with the address coordinates
    diagnose_zone_issue(35.2271, -80.8431, "1010 Kenilworth Ave, Charlotte, NC")
