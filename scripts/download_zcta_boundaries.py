"""Download ZCTA boundaries from Census Bureau and store locally."""
import requests
import json
import os
from pathlib import Path

# Create boundaries directory
BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def download_zcta_boundary(zip_code):
    """Download a single ZCTA boundary from Census TIGERweb."""
    # Census TIGERweb REST API endpoint
    base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/82/query"
    
    # Try different query formats
    queries = [
        f"ZCTA5 = '{zip_code}'",
        f"ZCTA5='{zip_code}'",
        f"ZCTA5CE10 = '{zip_code}'",
    ]
    
    for where_clause in queries:
        params = {
            'where': where_clause,
            'outFields': '*',
            'f': 'geojson',
            'outSR': '4326',
            'returnGeometry': 'true'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and len(data['features']) > 0:
                    # Save to file
                    file_path = BOUNDARIES_DIR / f"{zip_code}.geojson"
                    with open(file_path, 'w') as f:
                        json.dump(data, f)
                    print(f"[SUCCESS] Downloaded boundary for {zip_code}")
                    return data
        except Exception as e:
            continue
    
    print(f"X Could not download boundary for {zip_code}")
    return None

def download_multiple_zctas(zip_codes):
    """Download boundaries for multiple zip codes."""
    results = {'success': 0, 'failed': 0}
    
    for zip_code in zip_codes:
        result = download_zcta_boundary(zip_code)
        if result:
            results['success'] += 1
        else:
            results['failed'] += 1
    
    print(f"\nDownload complete: {results['success']} success, {results['failed']} failed")
    return results

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Download specific zip codes
        zip_codes = sys.argv[1:]
        download_multiple_zctas(zip_codes)
    else:
        print("Usage: python download_zcta_boundaries.py <zip1> <zip2> ...")
        print("Example: python download_zcta_boundaries.py 28204 10001 90210")

