"""Check the status of the school data import."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData
from sqlalchemy import func

def check_import_status():
    """Display current import status."""
    db = SessionLocal()
    
    try:
        # Get total count
        total_schools = db.query(SchoolData).count()
        
        # Get schools with ratings
        schools_with_elem = db.query(SchoolData).filter(
            SchoolData.elementary_school_rating.isnot(None)
        ).count()
        schools_with_middle = db.query(SchoolData).filter(
            SchoolData.middle_school_rating.isnot(None)
        ).count()
        schools_with_high = db.query(SchoolData).filter(
            SchoolData.high_school_rating.isnot(None)
        ).count()
        
        # Get latest import time
        latest = db.query(func.max(SchoolData.created_at)).scalar()
        
        # Calculate cost (assuming $0.02 per school)
        cost_per_school = 0.02
        estimated_cost = total_schools * cost_per_school
        
        # Expected total (from estimate)
        expected_total = 4000
        progress_percent = (total_schools / expected_total * 100) if expected_total > 0 else 0
        
        print("=" * 60)
        print("SCHOOL DATA IMPORT STATUS")
        print("=" * 60)
        print(f"\nTotal Schools Imported: {total_schools:,}")
        print(f"Expected Total: ~{expected_total:,} schools")
        print(f"Progress: {progress_percent:.1f}%")
        print(f"\nSchools with Ratings:")
        print(f"  - Elementary: {schools_with_elem:,}")
        print(f"  - Middle: {schools_with_middle:,}")
        print(f"  - High: {schools_with_high:,}")
        print(f"\nEstimated Cost So Far: ${estimated_cost:.2f}")
        if latest:
            print(f"\nLast Import: {latest}")
        else:
            print(f"\nLast Import: No imports yet")
        
        # Show recent schools
        print(f"\n{'='*60}")
        print("Recent Schools (Last 5):")
        print("=" * 60)
        recent = db.query(SchoolData).order_by(SchoolData.created_at.desc()).limit(5).all()
        for school in recent:
            ratings = []
            if school.elementary_school_rating:
                ratings.append(f"Elem:{school.elementary_school_rating}")
            if school.middle_school_rating:
                ratings.append(f"Mid:{school.middle_school_rating}")
            if school.high_school_rating:
                ratings.append(f"High:{school.high_school_rating}")
            ratings_str = ", ".join(ratings) if ratings else "No ratings"
            print(f"  - {school.elementary_school_name or school.middle_school_name or school.high_school_name or 'Unknown'}")
            print(f"    Ratings: {ratings_str}")
            print(f"    Location: ({school.latitude:.4f}, {school.longitude:.4f})")
            print()
        
        print("=" * 60)
        
        # Status message
        if total_schools >= expected_total * 0.95:
            print("\n[COMPLETE] Import appears to be COMPLETE!")
        elif total_schools > 0:
            print(f"\n[IN PROGRESS] Import is IN PROGRESS ({progress_percent:.1f}% complete)")
        else:
            print("\n[WARNING] No schools imported yet. Run the import script first.")
        
    finally:
        db.close()

if __name__ == '__main__':
    check_import_status()
