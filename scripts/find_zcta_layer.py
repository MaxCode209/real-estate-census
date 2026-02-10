"""Find the correct layer number for ZCTA in Census TIGERweb."""
import requests
import json

base_url = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer'

print("Checking TIGERweb service for ZCTA layer...\n")

try:
    # Get service info
    response = requests.get(base_url, params={'f': 'json'}, timeout=30)
    if response.status_code == 200:
        data = response.json()
        layers = data.get('layers', [])
        
        print(f"Found {len(layers)} layers. Searching for ZCTA...\n")
        
        for layer in layers:
            layer_id = layer.get('id')
            layer_name = layer.get('name', '')
            
            # Check if it's ZCTA related
            if 'ZCTA' in layer_name.upper() or 'ZIP' in layer_name.upper() or 'ZIP CODE' in layer_name.upper():
                print(f"FOUND ZCTA LAYER:")
                print(f"  ID: {layer_id}")
                print(f"  Name: {layer_name}")
                print(f"  URL: {base_url}/{layer_id}")
                
                # Get layer details
                layer_url = f"{base_url}/{layer_id}"
                layer_response = requests.get(layer_url, params={'f': 'json'}, timeout=30)
                if layer_response.status_code == 200:
                    layer_data = layer_response.json()
                    print(f"\n  Fields:")
                    for field in layer_data.get('fields', [])[:10]:  # Show first 10
                        print(f"    - {field.get('name')} ({field.get('type')})")
                
                print("\n" + "="*70)
except Exception as e:
    print(f"Error: {e}")
