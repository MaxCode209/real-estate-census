"""
Batch download zip code boundaries for your database zip codes.
Downloads from FREE sources and saves locally.
"""
import sys
import os
import requests
import json
import time
from pathlib import Path
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def get_zip_codes_from_database(limit=None):
    """Get zip codes from database."""
    db = SessionLocal()
    try:
        query = db.query(CensusData).distinct(CensusData.zip_code)
        if limit:
            query = query.limit(limit)
        records = query.all()
        return [record.zip_code for record in records]
    finally:
        db.close()

def download_from_github_cdn(zip_code):
    """Try downloading from free GitHub CDN."""
    sources = [
        f"https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/zcta5/{zip_code}_polygon.geojson",
        f"https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/{zip_code[0]}/{zip_code}_polygon.geojson",
    ]
    
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'type' in data:
                    # Save it
                    file_path = BOUNDARIES_DIR / f"{zip_code}.geojson"
                    if data['type'] == 'Feature':
                        data = {'type': 'FeatureCollection', 'features': [data]}
                    with open(file_path, 'w') as f:
                        json.dump(data, f)
                    return True
        except:
            continue
    return False

def download_boundary(zip_code):
    """Download boundary for a single zip code."""
    # Check if already exists
    file_path = BOUNDARIES_DIR / f"{zip_code}.geojson"
    if file_path.exists():
        return True, "already_exists"
    
    # Try GitHub CDN (free)
    if download_from_github_cdn(zip_code):
        return True, "github"
    
    return False, "not_found"

def batch_download(zip_codes, batch_size=10, delay=1):
    """Download boundaries in batches."""
    total = len(zip_codes)
    success = 0
    already_exists = 0
    failed = []
    
    print(f"\nDownloading boundaries for {total} zip codes...")
    print("=" * 70)
    
    for i, zip_code in enumerate(zip_codes, 1):
        status, source = download_boundary(zip_code)
        
        if status:
            if source == "already_exists":
                already_exists += 1
                print(f"[{i}/{total}] {zip_code}: Already exists")
            else:
                success += 1
                print(f"[{i}/{total}] {zip_code}: Downloaded from {source}")
        else:
            failed.append(zip_code)
            print(f"[{i}/{total}] {zip_code}: Not found in free sources")
        
        # Rate limiting
        if i % batch_size == 0:
            time.sleep(delay)
            print(f"Progress: {i}/{total} ({i*100//total}%)")
    
    print("\n" + "=" * 70)
    print(f"Download Summary:")
    print(f"  Successfully downloaded: {success}")
    print(f"  Already existed: {already_exists}")
    print(f"  Not found: {len(failed)}")
    
    if failed:
        print(f"\nZip codes not found in free sources ({len(failed)}):")
        print(", ".join(failed[:20]) + ("..." if len(failed) > 20 else ""))
        print("\nFor these, you can:")
        print("1. Download manually from Census Bureau")
        print("2. Use Mapshaper (mapshaper.org) to extract from shapefile")
        print("3. They will use approximate boundaries for now")
    
    return success, already_exists, len(failed)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Download zip code boundaries in batch')
    parser.add_argument('--limit', type=int, help='Limit number of zip codes to process')
    parser.add_argument('--zip-codes', nargs='+', help='Specific zip codes to download')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for rate limiting')
    
    args = parser.parse_args()
    
    if args.zip_codes:
        zip_codes = args.zip_codes
    else:
        zip_codes = get_zip_codes_from_database(limit=args.limit)
    
    if not zip_codes:
        print("No zip codes found in database.")
        sys.exit(1)
    
    print(f"Found {len(zip_codes)} zip codes to process")
    
    # Ask for confirmation if processing many
    if len(zip_codes) > 50:
        response = input(f"\nProcess {len(zip_codes)} zip codes? This may take a while. (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    success, exists, failed = batch_download(zip_codes, batch_size=args.batch_size)
    
    print(f"\n[COMPLETE] Boundaries ready: {success + exists}/{len(zip_codes)}")
    print(f"Saved to: {BOUNDARIES_DIR}/")

