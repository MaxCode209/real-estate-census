"""Download ZCTA boundaries from Census Bureau (100% FREE)."""
import requests
import zipfile
import json
import sys
import os
from pathlib import Path
import tempfile

# Census Bureau provides ZCTA boundaries as shapefiles - FREE
CENSUS_ZCTA_URL = "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA5/tl_2024_us_zcta510.zip"

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def download_census_zcta_shapefile():
    """Download the full ZCTA shapefile from Census (FREE, official)."""
    print("Downloading Census ZCTA shapefile (this may take a few minutes)...")
    print("This is a large file (~50MB) but it's completely FREE from the US government.")
    
    try:
        response = requests.get(CENSUS_ZCTA_URL, stream=True, timeout=300)
        if response.status_code == 200:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            print(f"Downloaded to: {tmp_path}")
            print("Note: To convert shapefiles to GeoJSON, you'll need:")
            print("  - ogr2ogr (from GDAL) or")
            print("  - Python library: geopandas or fiona")
            print("\nAlternatively, use the web-based approach below.")
            
            return tmp_path
        else:
            print(f"Download failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

def extract_zip_code_from_shapefile(zip_code, shapefile_path):
    """Extract specific zip code from shapefile (requires GDAL/ogr2ogr)."""
    # This would require ogr2ogr command-line tool
    # For now, we'll use a web-based approach
    pass

if __name__ == '__main__':
    print("=" * 60)
    print("FREE Census ZCTA Boundary Downloader")
    print("=" * 60)
    print("\nOption 1: Download full shapefile (requires conversion tools)")
    print("Option 2: Use web-based GeoJSON converter (easier)")
    print("\nFor now, let's use a simpler approach...")
    print("\nActually, the BEST free solution is to use a pre-processed")
    print("GeoJSON service or download boundaries on-demand.")
    print("\nLet me implement an on-demand downloader that works...")

