"""
Download accurate zip code boundaries from Census TIGERweb.
This is the OFFICIAL source for ZCTA (Zip Code Tabulation Area) boundaries.
"""
import sys
import os
import requests
import json
import time
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def get_zip_codes_from_database(limit=None):
    """Get all unique zip codes from database."""
    db = SessionLocal()
    try:
        query = db.query(CensusData.zip_code).distinct()
        if limit:
            query = query.limit(limit)
        results = query.all()
        return [row[0] for row in results]
    finally:
        db.close()

def download_from_census_tigerweb(zip_code: str) -> Tuple[bool, str]:
    """
    Download boundary from Census TIGERweb (OFFICIAL source).
    Returns: (success, message)
    """
    # Check if already exists
    file_path = BOUNDARIES_DIR / f"{zip_code}.geojson"
    if file_path.exists():
        return True, "already_exists"
    
    # Census TIGERweb REST API endpoints (ZCTA layer is 2, not 82!)
    endpoints = [
        "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/2/query",
        "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2022/MapServer/2/query",
        "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2021/MapServer/2/query",
    ]
    
    # Try different query formats
    where_clauses = [
        f"ZCTA5='{zip_code}'",
        f"ZCTA5 = '{zip_code}'",
        f"ZCTA5CE10='{zip_code}'",
        f"ZCTA5CE10 = '{zip_code}'",
    ]
    
    for endpoint in endpoints:
        for where_clause in where_clauses:
            try:
                params = {
                    'where': where_clause,
                    'outFields': '*',
                    'f': 'geojson',
                    'outSR': '4326',
                    'returnGeometry': 'true'
                }
                
                response = requests.get(endpoint, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response has features
                    if 'features' in data and isinstance(data['features'], list) and len(data['features']) > 0:
                        feature = data['features'][0]
                        
                        # Validate it's actually a polygon
                        if 'geometry' in feature:
                            geometry = feature['geometry']
                            if geometry.get('type') in ['Polygon', 'MultiPolygon']:
                                # Save to file
                                with open(file_path, 'w') as f:
                                    json.dump(data, f)
                                return True, "census_tigerweb"
                
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.RequestException:
                continue
            except Exception as e:
                continue
    
    return False, "not_found"

def batch_download(zip_codes: List[str], delay: float = 0.5):
    """
    Download boundaries for all zip codes.
    delay: seconds to wait between requests (to avoid rate limiting)
    """
    total = len(zip_codes)
    success = 0
    already_exists = 0
    failed = []
    
    print(f"\n{'='*70}")
    print(f"Downloading accurate boundaries from Census TIGERweb")
    print(f"Total zip codes: {total}")
    print(f"{'='*70}\n")
    
    for i, zip_code in enumerate(zip_codes, 1):
        status, message = download_from_census_tigerweb(zip_code)
        
        if status:
            if message == "already_exists":
                already_exists += 1
                print(f"[{i:4d}/{total}] {zip_code}: [OK] Already exists")
            else:
                success += 1
                print(f"[{i:4d}/{total}] {zip_code}: [OK] Downloaded from Census")
        else:
            failed.append(zip_code)
            print(f"[{i:4d}/{total}] {zip_code}: [FAIL] Not found")
        
        # Rate limiting - be nice to Census servers
        if i < total:
            time.sleep(delay)
        
        # Progress update every 50
        if i % 50 == 0:
            print(f"\nProgress: {i}/{total} ({i*100//total}%) | Success: {success} | Failed: {len(failed)}\n")
    
    print(f"\n{'='*70}")
    print(f"DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully downloaded: {success}")
    print(f"Already existed: {already_exists}")
    print(f"Not found: {len(failed)}")
    print(f"Total with boundaries: {success + already_exists}/{total}")
    print(f"\nBoundaries saved to: {BOUNDARIES_DIR.absolute()}")
    
    if failed:
        print(f"\n[WARNING] {len(failed)} zip codes not found:")
        if len(failed) <= 20:
            print(", ".join(failed))
        else:
            print(", ".join(failed[:20]) + f" ... and {len(failed) - 20} more")
        print("\nThese will use approximate boundaries (rectangles) on the map.")
    
    return success, already_exists, len(failed)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download accurate zip code boundaries from Census TIGERweb',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all zip codes from database
  python scripts/download_accurate_boundaries.py
  
  # Download specific zip codes
  python scripts/download_accurate_boundaries.py --zip-codes 28204 10001 90210
  
  # Download first 100 zip codes (for testing)
  python scripts/download_accurate_boundaries.py --limit 100
        """
    )
    parser.add_argument('--limit', type=int, help='Limit number of zip codes to process')
    parser.add_argument('--zip-codes', nargs='+', help='Specific zip codes to download')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests (seconds)')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.zip_codes:
        zip_codes = args.zip_codes
    else:
        zip_codes = get_zip_codes_from_database(limit=args.limit)
    
    if not zip_codes:
        print("[ERROR] No zip codes found in database.")
        sys.exit(1)
    
    print(f"[INFO] Found {len(zip_codes)} zip codes to process")
    
    # Ask for confirmation if processing many
    if len(zip_codes) > 50 and not args.yes:
        print(f"\n[WARNING] This will download boundaries for {len(zip_codes)} zip codes.")
        print(f"   Estimated time: ~{len(zip_codes) * args.delay / 60:.1f} minutes")
        response = input(f"\nContinue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    success, exists, failed = batch_download(zip_codes, delay=args.delay)
    
    print(f"\n[SUCCESS] Complete! {success + exists}/{len(zip_codes)} zip codes now have accurate boundaries.")
    print(f"   Refresh your map to see the accurate shapes!")
