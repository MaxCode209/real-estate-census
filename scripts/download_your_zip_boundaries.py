"""
Download boundaries for zip codes in your database.
This only downloads the ones you actually need - much faster!
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def get_zip_codes_from_database():
    """Get all zip codes from your database."""
    db = SessionLocal()
    try:
        records = db.query(CensusData).all()
        zip_codes = [record.zip_code for record in records]
        return zip_codes
    finally:
        db.close()

def print_instructions(zip_codes):
    """Print instructions for downloading boundaries."""
    print("=" * 70)
    print("Download Boundaries for Your Zip Codes")
    print("=" * 70)
    print(f"\nYou have {len(zip_codes)} zip codes in your database.")
    print("\nTo get boundaries for all of them:")
    print("\n1. Download Census ZCTA shapefile:")
    print("   https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html")
    print("   Look for: 'ZIP Code Tabulation Areas (ZCTAs)'")
    print("\n2. Use Mapshaper (free, online, no signup):")
    print("   https://mapshaper.org/")
    print("   - Upload the shapefile zip")
    print("   - In console, type:")
    sample_zips = '","'.join(zip_codes[:10])
    print(f'     filter "ZCTA5CE10 in ["{sample_zips}"...]"')
    print("   - Export as GeoJSON")
    print("   - Split by zip code and save individually")
    print("\n3. Or use this Python script (requires geopandas):")
    print("   python scripts/auto_download_boundaries.py " + " ".join(zip_codes[:5]) + " ...")
    print("\n4. Save files to: data/zip_boundaries/{zip_code}.geojson")
    print("\nOnce boundaries are in that folder, the app will use them automatically!")

if __name__ == '__main__':
    zip_codes = get_zip_codes_from_database()
    print_instructions(zip_codes)
    
    print(f"\nYour zip codes ({len(zip_codes)} total):")
    print(", ".join(zip_codes[:20]) + ("..." if len(zip_codes) > 20 else ""))

