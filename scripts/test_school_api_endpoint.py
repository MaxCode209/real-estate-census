"""Test the school API endpoint directly."""
import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

def test_school_api():
    """Test the /api/schools/address endpoint."""
    print("Testing School API Endpoint")
    print("=" * 60)
    
    # Test with a known address
    test_address = "123 Main St, New York, NY 10001"
    test_lat = 40.7128
    test_lng = -74.0060
    
    print(f"\nTesting with address: {test_address}")
    print(f"Coordinates: ({test_lat}, {test_lng})")
    print("\nCalling API endpoint...")
    
    url = f"http://localhost:5000/api/schools/address"
    params = {
        'address': test_address,
        'lat': test_lat,
        'lng': test_lng
    }
    
    try:
        print(f"\nRequest URL: {url}")
        print(f"Parameters: {params}")
        
        # Make request with longer timeout (Apify can take 30-60 seconds)
        response = requests.get(url, params=params, timeout=120)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        data = response.json()
        print(f"\nResponse Data:")
        print(json.dumps(data, indent=2))
        
        # Check if we got ratings
        if data.get('elementary_school_rating'):
            print(f"\n[SUCCESS] Elementary rating: {data['elementary_school_rating']}")
        else:
            print(f"\n[WARNING] No elementary rating found")
        
        if data.get('middle_school_rating'):
            print(f"[SUCCESS] Middle rating: {data['middle_school_rating']}")
        else:
            print(f"[WARNING] No middle rating found")
        
        if data.get('high_school_rating'):
            print(f"[SUCCESS] High rating: {data['high_school_rating']}")
        else:
            print(f"[WARNING] No high rating found")
        
        if data.get('blended_school_score'):
            print(f"[SUCCESS] Blended score: {data['blended_school_score']}")
        else:
            print(f"[WARNING] No blended score found")
        
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out (Apify takes 30-60 seconds)")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_school_api()
    sys.exit(0 if success else 1)
