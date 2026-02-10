"""
Check how many zip code boundaries you have locally and compare with database.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

BOUNDARIES_DIR = Path('data/zip_boundaries')

def check_coverage():
    """Check zip boundary coverage."""
    print("="*70)
    print("ZIP CODE BOUNDARY COVERAGE REPORT")
    print("="*70)
    
    # Get all zip codes from database
    db = SessionLocal()
    try:
        db_zip_codes = set(row[0] for row in db.query(CensusData.zip_code).distinct().all())
        print(f"\n[1] Zip codes in database: {len(db_zip_codes)}")
    finally:
        db.close()
    
    # Get all local boundary files
    if not BOUNDARIES_DIR.exists():
        print(f"\n[2] Local boundaries directory does not exist: {BOUNDARIES_DIR}")
        local_zip_codes = set()
    else:
        local_files = list(BOUNDARIES_DIR.glob('*.geojson'))
        local_zip_codes = {f.stem for f in local_files}
        print(f"[2] Local boundary files: {len(local_zip_codes)}")
    
    # Calculate coverage
    if db_zip_codes:
        missing = db_zip_codes - local_zip_codes
        coverage_pct = (len(local_zip_codes) / len(db_zip_codes)) * 100
        
        print(f"\n[3] Coverage: {len(local_zip_codes)}/{len(db_zip_codes)} ({coverage_pct:.1f}%)")
        print(f"[4] Missing boundaries: {len(missing)}")
        
        if missing:
            print(f"\n[5] Missing zip codes (first 20):")
            for zip_code in sorted(list(missing))[:20]:
                print(f"    - {zip_code}")
            if len(missing) > 20:
                print(f"    ... and {len(missing) - 20} more")
            
            print(f"\n[6] To download missing boundaries:")
            print(f"    python scripts/download_accurate_boundaries.py")
            print(f"    (This will download all missing boundaries from Census TIGERweb)")
        else:
            print(f"\n[5] ✓ All zip codes in database have boundary files!")
    else:
        print(f"\n[3] No zip codes in database to check coverage against.")
    
    # Check for extra files (not in database)
    if db_zip_codes:
        extra = local_zip_codes - db_zip_codes
        if extra:
            print(f"\n[7] Extra boundary files (not in database): {len(extra)}")
            print(f"    These are fine to keep - they may be used for future zip codes.")
    
    print("\n" + "="*70)
    print("REPORT COMPLETE")
    print("="*70)

if __name__ == '__main__':
    check_coverage()
