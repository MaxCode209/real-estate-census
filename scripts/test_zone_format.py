"""Test script to check the format of zone boundaries in the database."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import AttendanceZone
from sqlalchemy import or_
import json

def test_zone_format():
    """Check the format of zone boundaries."""
    db = SessionLocal()
    try:
        # Get a few sample zones
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).limit(5).all()
        
        print(f"Checking {len(zones)} sample zones...")
        print("=" * 80)
        
        for i, zone in enumerate(zones, 1):
            print(f"\nZone {i}: {zone.school_name} ({zone.school_level}, {zone.state})")
            
            # Check raw zone_boundary (should be JSON string)
            raw_boundary = zone.zone_boundary
            print(f"  Raw type: {type(raw_boundary)}")
            if isinstance(raw_boundary, str):
                print(f"  Raw length: {len(raw_boundary)} chars")
                try:
                    parsed = json.loads(raw_boundary)
                    print(f"  Parsed type: {type(parsed)}")
                    if isinstance(parsed, dict):
                        print(f"  Parsed keys: {list(parsed.keys())}")
                        if 'type' in parsed:
                            print(f"  Geometry type: {parsed['type']}")
                        if 'coordinates' in parsed:
                            coords = parsed['coordinates']
                            if isinstance(coords, list):
                                print(f"  Coordinates: list with {len(coords)} elements")
                except Exception as e:
                    print(f"  Error parsing: {e}")
            
            # Check to_dict() output
            zone_dict = zone.to_dict()
            boundary_in_dict = zone_dict.get('zone_boundary')
            print(f"  In to_dict(): type={type(boundary_in_dict)}")
            if isinstance(boundary_in_dict, dict):
                print(f"  In to_dict(): keys={list(boundary_in_dict.keys())}")
                if 'type' in boundary_in_dict:
                    print(f"  In to_dict(): geometry type={boundary_in_dict['type']}")
            
            print("-" * 80)
        
    finally:
        db.close()

if __name__ == '__main__':
    test_zone_format()
