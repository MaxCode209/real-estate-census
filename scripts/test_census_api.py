"""Test Census TIGERweb API to see what's happening."""
import requests
import json

zip_code = '28204'
url = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/82/query'

# Try different query formats
queries = [
    f"ZCTA5='{zip_code}'",
    f"ZCTA5 = '{zip_code}'",
    f"ZCTA5CE10='{zip_code}'",
    f"ZCTA5CE10 = '{zip_code}'",
]

for where_clause in queries:
    print(f"\nTrying: {where_clause}")
    params = {
        'where': where_clause,
        'outFields': '*',
        'f': 'json',
        'outSR': '4326',
        'returnGeometry': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'features' in data:
                print(f"Features count: {len(data['features'])}")
                if len(data['features']) > 0:
                    feature = data['features'][0]
                    print(f"Feature keys: {list(feature.keys())}")
                    if 'geometry' in feature:
                        print(f"Geometry type: {feature['geometry'].get('type')}")
                        print("SUCCESS!")
                        break
                    else:
                        print("No geometry in feature")
                        print(f"Feature: {json.dumps(feature, indent=2)[:500]}")
                else:
                    print("No features in response")
                    if 'error' in data:
                        print(f"Error: {data['error']}")
            else:
                print("No 'features' key in response")
                print(f"Response: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"Error response: {response.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")
