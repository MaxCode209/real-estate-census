"""Test zip code boundary fetching."""
import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_boundary_api(zip_code='28204'):
    """Test the zip boundary API endpoint."""
    print(f"Testing boundary API for zip code: {zip_code}")
    print("=" * 50)
    
    # Test backend endpoint
    try:
        response = requests.get(f'http://localhost:5000/api/zip-boundary/{zip_code}', timeout=15)
        print(f"Backend API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Got GeoJSON with {len(data.get('features', []))} features")
            if data.get('features'):
                geom = data['features'][0].get('geometry', {})
                print(f"Geometry type: {geom.get('type')}")
                if geom.get('type') == 'Polygon':
                    coords = geom.get('coordinates', [])
                    if coords:
                        print(f"Polygon has {len(coords[0])} coordinate points")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Backend API Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing direct sources:")
    
    # Test OpenDataSoft directly
    try:
        url = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/us-zip-code-labels-and-boundaries/records"
        params = {'where': f'zcta5ce10="{zip_code}"', 'limit': 1}
        response = requests.get(url, params=params, timeout=15)
        print(f"OpenDataSoft Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                print("OpenDataSoft: Found data!")
                fields = data['results'][0].get('record', {}).get('fields', {})
                if 'geo_shape' in fields:
                    print("OpenDataSoft: Has geo_shape!")
                else:
                    print("OpenDataSoft: No geo_shape field")
            else:
                print("OpenDataSoft: No results")
    except Exception as e:
        print(f"OpenDataSoft Error: {e}")

if __name__ == '__main__':
    test_boundary_api('28204')

