"""Check what fields are available in Census TIGERweb layer."""
import requests
import json

# Get layer info
url = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/82'

print("Checking layer metadata...")
print(f"URL: {url}\n")

try:
    # Get layer info
    response = requests.get(url, params={'f': 'json'}, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print("Layer Name:", data.get('name', 'N/A'))
        print("\nFields:")
        for field in data.get('fields', []):
            print(f"  - {field.get('name')} ({field.get('type')})")
        
        print("\n\nTrying to query with objectIds...")
        # Try querying by objectIds instead
        query_url = url + '/query'
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'json',
            'returnGeometry': 'false',
            'resultRecordCount': 5
        }
        response2 = requests.get(query_url, params=params, timeout=30)
        if response2.status_code == 200:
            data2 = response2.json()
            if 'features' in data2 and len(data2['features']) > 0:
                print("Sample record fields:")
                sample = data2['features'][0]
                if 'attributes' in sample:
                    for key, value in sample['attributes'].items():
                        print(f"  {key}: {value}")
except Exception as e:
    print(f"Error: {e}")
