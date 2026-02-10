"""Check what school names are in the database for Charlotte area."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData
from sqlalchemy import or_

def check_charlotte_schools():
    """Check school names in database for Charlotte area."""
    db = SessionLocal()
    try:
        # Get schools near Charlotte (lat ~35.2, lng ~-80.8)
        schools = db.query(SchoolData).filter(
            SchoolData.latitude.between(35.0, 35.5),
            SchoolData.longitude.between(-81.0, -80.5)
        ).limit(20).all()
        
        print(f"Found {len(schools)} schools in Charlotte area")
        print("=" * 80)
        
        for school in schools:
            print(f"\nAddress: {school.address}")
            print(f"  Elementary: {school.elementary_school_name} (Rating: {school.elementary_school_rating})")
            print(f"  Middle: {school.middle_school_name} (Rating: {school.middle_school_rating})")
            print(f"  High: {school.high_school_name} (Rating: {school.high_school_rating})")
        
        # Check for specific schools
        print("\n" + "=" * 80)
        print("Searching for 'Ashley Park' and 'West Charlotte'...")
        
        ashley = db.query(SchoolData).filter(
            SchoolData.elementary_school_name.ilike('%Ashley Park%')
        ).all()
        print(f"\nFound {len(ashley)} schools with 'Ashley Park':")
        for s in ashley:
            print(f"  - {s.elementary_school_name}")
        
        west_charlotte = db.query(SchoolData).filter(
            SchoolData.high_school_name.ilike('%West Charlotte%')
        ).all()
        print(f"\nFound {len(west_charlotte)} schools with 'West Charlotte':")
        for s in west_charlotte:
            print(f"  - {s.high_school_name}")
        
    finally:
        db.close()

if __name__ == '__main__':
    check_charlotte_schools()
