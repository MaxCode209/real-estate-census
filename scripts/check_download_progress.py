"""Check progress of ongoing downloads."""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData

def check_progress():
    """Check progress of all downloads."""
    print("="*80)
    print("DOWNLOAD PROGRESS STATUS")
    print("="*80)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check zip boundary download
    print("[1] ZIP BOUNDARY DOWNLOAD")
    print("-" * 80)
    boundaries_dir = Path('data/zip_boundaries')
    
    if boundaries_dir.exists():
        boundary_files = list(boundaries_dir.glob('*.geojson'))
        total_files = len(boundary_files)
        started_with = 804
        new_downloaded = total_files - started_with
        missing_total = 12864
        remaining = missing_total - new_downloaded
        progress_pct = (new_downloaded / missing_total * 100) if missing_total > 0 else 0
        
        print(f"  Total boundary files: {total_files:,}")
        print(f"  Started with: {started_with:,}")
        print(f"  New downloaded: {new_downloaded:,}")
        print(f"  Remaining: {remaining:,}")
        print(f"  Progress: {progress_pct:.1f}%")
        
        # Estimate time remaining (assuming ~33 per minute rate)
        if new_downloaded > 0:
            rate_per_min = 33.0  # Approximate rate
            minutes_remaining = remaining / rate_per_min if rate_per_min > 0 else 0
            hours_remaining = minutes_remaining / 60
            print(f"  Estimated time remaining: ~{hours_remaining:.1f} hours ({minutes_remaining:.0f} minutes)")
    else:
        print("  ERROR: Boundaries directory not found!")
    
    # Check school data
    print("\n[2] SCHOOL DATA STATUS")
    print("-" * 80)
    db = SessionLocal()
    try:
        total_schools = db.query(SchoolData).count()
        schools_with_elem = db.query(SchoolData).filter(
            SchoolData.elementary_school_rating.isnot(None)
        ).count()
        schools_with_mid = db.query(SchoolData).filter(
            SchoolData.middle_school_rating.isnot(None)
        ).count()
        schools_with_high = db.query(SchoolData).filter(
            SchoolData.high_school_rating.isnot(None)
        ).count()
        
        print(f"  Total schools in database: {total_schools:,}")
        print(f"  With elementary ratings: {schools_with_elem:,}")
        print(f"  With middle ratings: {schools_with_mid:,}")
        print(f"  With high ratings: {schools_with_high:,}")
    finally:
        db.close()
    
    # Check if processes are still running (basic check)
    print("\n[3] PROCESS STATUS")
    print("-" * 80)
    print("  Note: Check terminal windows or task manager for actual process status")
    print("  Boundary download: Should be running in background")
    print("  School import: Completed (one-time run)")
    
    print("\n" + "="*80)
    print("To check again, run: python scripts/check_download_progress.py")
    print("="*80)

if __name__ == '__main__':
    check_progress()
