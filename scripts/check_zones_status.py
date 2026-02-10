"""Check attendance zones status in database."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import AttendanceZone

db = SessionLocal()

try:
    total = db.query(AttendanceZone).count()
    print(f"Total zones in database: {total}")
    
    if total > 0:
        zones = db.query(AttendanceZone).limit(10).all()
        print("\nSample zones:")
        for z in zones:
            print(f"  Name: {z.school_name[:60] if z.school_name else 'None'}")
            print(f"    Level: {z.school_level}, State: {z.state}")
        
        unknown = db.query(AttendanceZone).filter(AttendanceZone.school_name == 'Unknown').count()
        print(f"\nZones with 'Unknown' name: {unknown} out of {total} ({unknown*100/total:.1f}%)")
        
        # Check by state
        nc_count = db.query(AttendanceZone).filter(AttendanceZone.state == 'NC').count()
        sc_count = db.query(AttendanceZone).filter(AttendanceZone.state == 'SC').count()
        print(f"\nBy state: NC={nc_count}, SC={sc_count}")
        
        # Check by level
        from sqlalchemy import func
        levels = db.query(AttendanceZone.school_level, func.count(AttendanceZone.id)).group_by(AttendanceZone.school_level).all()
        print("\nBy school level:")
        for level, count in levels:
            print(f"  {level}: {count}")
    else:
        print("\nNo zones found. The import may not have completed yet.")
        print("Run: python scripts/import_nces_zones.py")
        
finally:
    db.close()
