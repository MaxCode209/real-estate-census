"""Fetch zip code boundaries from FREE sources."""
import requests
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def fetch_from_census_tigerweb(zip_code):
    """Fetch from Census TIGERweb - FREE official source."""
    # Try the correct Census TIGERweb format
    base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/82/query"
    
    # Census uses ZCTA5 format - need to query correctly
    # Try different field names and formats
    queries = [
        {"where": f"ZCTA5='{zip_code}'", "outFields": "ZCTA5"},
        {"where": f"ZCTA5 = '{zip_code}'", "outFields": "ZCTA5"},
        {"where": f"ZCTA5CE10='{zip_code}'", "outFields": "ZCTA5CE10"},
    ]
    
    for query_params in queries:
        params = {
            **query_params,
            'f': 'geojson',
            'outSR': '4326',
            'returnGeometry': 'true'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Check if we got features
                if 'features' in data and len(data['features']) > 0:
                    return data
                # Check for error
                if 'error' in data:
                    print(f"Census error: {data['error']}")
        except Exception as e:
            continue
    
    return None

def fetch_from_github_cdn(zip_code):
    """Fetch from free GitHub CDN."""
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
                    if data['type'] == 'Feature':
                        return {'type': 'FeatureCollection', 'features': [data]}
                    return data
        except:
            continue
    
    return None

def fetch_and_save(zip_code):
    """Fetch boundary and save locally."""
    print(f"Fetching boundary for {zip_code}...")
    
    # Try Census first (most reliable)
    data = fetch_from_census_tigerweb(zip_code)
    
    # Try GitHub if Census fails
    if not data:
        data = fetch_from_github_cdn(zip_code)
    
    if data:
        # Save locally
        file_path = BOUNDARIES_DIR / f"{zip_code}.geojson"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print(f"[SUCCESS] Saved boundary for {zip_code}")
        return True
    else:
        print(f"[FAILED] Could not fetch boundary for {zip_code}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        zip_codes = sys.argv[1:]
        success = 0
        for zc in zip_codes:
            if fetch_and_save(zc):
                success += 1
        print(f"\nCompleted: {success}/{len(zip_codes)} successful")
    else:
        print("Usage: python fetch_free_boundaries.py <zip1> <zip2> ...")
        print("Example: python fetch_free_boundaries.py 28204 10001")

