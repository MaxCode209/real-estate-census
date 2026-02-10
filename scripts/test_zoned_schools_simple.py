"""Simple test script - uses hardcoded coordinates to test logic."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import AttendanceZone, SchoolData
from backend.zone_utils import find_zoned_schools
from sqlalchemy import or_

def test_with_coordinates(lat, lng, address_name="Test Address"):
    """Test zoned schools logic with specific coordinates."""
    print("=" * 80)
    print(f"TESTING: {address_name}")
    print(f"Coordinates: lat={lat}, lng={lng}")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Step 1: Try attendance zones
        print("\n[STEP 1] Testing attendance zones (point-in-polygon)...")
        zones = db.query(AttendanceZone).filter(
            or_(
                AttendanceZone.state == 'NC',
                AttendanceZone.state == 'SC'
            )
        ).all()
        
        print(f"  [OK] Loaded {len(zones)} zones from database")
        
        zoned_elementary = None
        zoned_middle = None
        zoned_high = None
        
        if zones:
            zones_list = [zone.to_dict() for zone in zones]
            print(f"  [OK] Converted to dict format")
            print(f"  Testing point-in-polygon...")
            
            zoned_elementary = find_zoned_schools(lat, lng, zones_list, 'elementary')
            zoned_middle = find_zoned_schools(lat, lng, zones_list, 'middle')
            zoned_high = find_zoned_schools(lat, lng, zones_list, 'high')
        
        use_zones = zoned_elementary or zoned_middle or zoned_high
        print(f"\n  Result: {'[OK] FOUND ZONED SCHOOLS' if use_zones else '[FAIL] NO ZONED SCHOOLS FOUND'}")
        print(f"    - Elementary: {zoned_elementary.get('school_name') if zoned_elementary else 'None'}")
        print(f"    - Middle: {zoned_middle.get('school_name') if zoned_middle else 'None'}")
        print(f"    - High: {zoned_high.get('school_name') if zoned_high else 'None'}")
        
        # Step 2: Match to database
        print("\n[STEP 2] Matching to database for ratings...")
        
        if use_zones:
            elementary_name = zoned_elementary.get('school_name') if zoned_elementary else None
            middle_name = zoned_middle.get('school_name') if zoned_middle else None
            high_name = zoned_high.get('school_name') if zoned_high else None
            
            # Match elementary - try multiple strategies
            if elementary_name:
                # 1. Exact match
                elem_school = db.query(SchoolData).filter(
                    SchoolData.elementary_school_name == elementary_name,
                    SchoolData.elementary_school_rating.isnot(None)
                ).first()
                
                # 2. Partial match
                if not elem_school:
                    elem_school = db.query(SchoolData).filter(
                        SchoolData.elementary_school_name.ilike(f'%{elementary_name}%'),
                        SchoolData.elementary_school_rating.isnot(None)
                    ).first()
                
                # 3. Clean name (remove suffixes)
                if not elem_school:
                    name_clean = elementary_name.replace(' School', '').replace(' Elementary', '').replace(' Elem', '').replace(' PreK-8', '').replace(' PreK', '').strip()
                    if name_clean and name_clean != elementary_name:
                        elem_school = db.query(SchoolData).filter(
                            SchoolData.elementary_school_name.ilike(f'%{name_clean}%'),
                            SchoolData.elementary_school_rating.isnot(None)
                        ).first()
                
                # 4. If zone has "PreK-8", search for "Elementary" version
                if not elem_school and 'PreK' in elementary_name:
                    name_base = elementary_name.replace(' PreK-8', '').replace(' PreK', '').replace(' School', '').strip()
                    if name_base:
                        elem_school = db.query(SchoolData).filter(
                            SchoolData.elementary_school_name.ilike(f'%{name_base}%Elementary%'),
                            SchoolData.elementary_school_rating.isnot(None)
                        ).first()
                
                if elem_school:
                    print(f"  [OK] Elementary: {elem_school.elementary_school_name} - Rating: {elem_school.elementary_school_rating}")
                else:
                    print(f"  [FAIL] Elementary: '{elementary_name}' - No rating found in database")
            
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
                    print(f"  [OK] Middle: {mid_school.middle_school_name} - Rating: {mid_school.middle_school_rating}")
                else:
                    print(f"  [FAIL] Middle: '{middle_name}' - No rating found in database")
            
            # Match high - try multiple strategies
            if high_name:
                # 1. Exact match
                high_school = db.query(SchoolData).filter(
                    SchoolData.high_school_name == high_name,
                    SchoolData.high_school_rating.isnot(None)
                ).first()
                
                # 2. Partial match
                if not high_school:
                    high_school = db.query(SchoolData).filter(
                        SchoolData.high_school_name.ilike(f'%{high_name}%'),
                        SchoolData.high_school_rating.isnot(None)
                    ).first()
                
                # 3. Clean name
                if not high_school:
                    name_clean = high_name.replace(' School', '').replace(' High', '').replace(' High School', '').strip()
                    if name_clean and name_clean != high_name:
                        high_school = db.query(SchoolData).filter(
                            SchoolData.high_school_name.ilike(f'%{name_clean}%'),
                            SchoolData.high_school_rating.isnot(None)
                        ).first()
                
                # 4. Search for key words
                if not high_school:
                    words = high_name.split()
                    if len(words) >= 2:
                        for term in [' '.join(words[:2]), ' '.join(words[:3])]:
                            high_school = db.query(SchoolData).filter(
                                SchoolData.high_school_name.ilike(f'%{term}%'),
                                SchoolData.high_school_rating.isnot(None)
                            ).first()
                            if high_school:
                                break
                
                if high_school:
                    print(f"  [OK] High: {high_school.high_school_name} - Rating: {high_school.high_school_rating}")
                else:
                    print(f"  [FAIL] High: '{high_name}' - No rating found in database")
                    # Show what's in database
                    similar = db.query(SchoolData).filter(
                        SchoolData.high_school_name.ilike('%Charlotte%')
                    ).limit(5).all()
                    if similar:
                        print(f"    Similar high schools in database:")
                        for s in similar:
                            print(f"      - {s.high_school_name}")
        else:
            print("  [FAIL] No zoned schools found - would use distance-based lookup")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if use_zones:
            print("[OK] USING ZONED SCHOOLS APPROACH")
        else:
            print("[FAIL] FALLING BACK TO DISTANCE-BASED (old method)")
        print("=" * 80)
        
    finally:
        db.close()

if __name__ == '__main__':
    # Test with known Charlotte coordinates
    # 1010 Kenilworth Ave, Charlotte, NC is approximately:
    test_with_coordinates(35.2271, -80.8431, "1010 Kenilworth Ave, Charlotte, NC")
    
    print("\n\n")
    # Test with another address if you want
    # test_with_coordinates(35.2088, -80.8307, "Another Charlotte Address")
