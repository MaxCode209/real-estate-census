"""Test script to verify Apify school scraper integration."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apify_client import ApifySchoolClient
from config.config import Config

def test_apify_connection():
    """Test basic Apify connection and school fetching."""
    print("Testing Apify School Scraper Integration")
    print("=" * 60)
    
    # Check API token
    if not Config.APIFY_API_TOKEN:
        print("ERROR: APIFY_API_TOKEN not set in .env file")
        return False
    
    print(f"[OK] API Token found: {Config.APIFY_API_TOKEN[:20]}...")
    
    # Test with a known address (New York City)
    test_address = "123 Main St, New York, NY 10001"
    test_lat = 40.7128
    test_lng = -74.0060
    
    print(f"\nTesting with address: {test_address}")
    print(f"Coordinates: ({test_lat}, {test_lng})")
    print("\nFetching schools (this may take 30-60 seconds)...")
    
    try:
        client = ApifySchoolClient()
        elementary, middle, high = client.get_schools_by_address(
            address=test_address,
            lat=test_lat,
            lng=test_lng,
            radius_miles=2.0
        )
        
        print("\n" + "=" * 60)
        print("RESULTS:")
        print("=" * 60)
        
        if elementary:
            print(f"\n[OK] Elementary School Found:")
            print(f"  Name: {elementary.get('schoolName', elementary.get('name', 'N/A'))}")
            print(f"  Rating: {elementary.get('gsRating', elementary.get('rating', 'N/A'))}")
            print(f"  Address: {elementary.get('address', 'N/A')}")
            print(f"  Full data: {elementary}")
        else:
            print("\n[ERROR] No elementary school found")
        
        if middle:
            print(f"\n[OK] Middle School Found:")
            print(f"  Name: {middle.get('schoolName', middle.get('name', 'N/A'))}")
            print(f"  Rating: {middle.get('gsRating', middle.get('rating', 'N/A'))}")
            print(f"  Address: {middle.get('address', 'N/A')}")
            print(f"  Full data: {middle}")
        else:
            print("\n[ERROR] No middle school found")
        
        if high:
            print(f"\n[OK] High School Found:")
            print(f"  Name: {high.get('schoolName', high.get('name', 'N/A'))}")
            print(f"  Rating: {high.get('gsRating', high.get('rating', 'N/A'))}")
            print(f"  Address: {high.get('address', 'N/A')}")
            print(f"  Full data: {high}")
        else:
            print("\n[ERROR] No high school found")
        
        if not elementary and not middle and not high:
            print("\n[WARNING] No schools found at all!")
            print("This could mean:")
            print("  - The Apify API call failed")
            print("  - No schools in the area")
            print("  - API credentials issue")
            print("  - Geographic bounds too small")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_apify_connection()
    sys.exit(0 if success else 1)
