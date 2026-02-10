"""
Test script to see all available fields for a zip code from Census API.
Tests zip code 20284 with 2023 data to see what fields are available.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config.config import Config

def test_census_api_fields(zip_code='20284', year='2022'):
    """Test what fields are available from Census API."""
    
    # Test 1: Get basic data (what we currently fetch)
    print("="*80)
    print(f"TESTING ZIP CODE: {zip_code} (Year: {year})")
    print("="*80)
    
    # Current variables we fetch
    current_variables = [
        'NAME',           # Geographic name
        'B01001_001E',    # Total Population
        'B01002_001E',    # Median Age
        'B19013_001E',    # Median Household Income
        'B19025_001E',    # Aggregate Household Income
        'B11001_001E',    # Total Households
    ]
    
    print("\n[1] CURRENT FIELDS WE FETCH:")
    print("-" * 80)
    url = f"{Config.CENSUS_API_BASE_URL}/{year}/{Config.CENSUS_DATASET}"
    # Try without 'in' parameter first (simpler geography)
    params = {
        'get': ','.join(current_variables),
        'for': f'zip code tabulation area:{zip_code}',
        'key': Config.CENSUS_API_KEY if Config.CENSUS_API_KEY else ''
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                headers = data[0]
                row = data[1]
                record = dict(zip(headers, row))
                
                print("Fields returned:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get list of ALL available variables
    print("\n[2] AVAILABLE VARIABLES IN ACS 5-YEAR DATASET:")
    print("-" * 80)
    print("Note: There are thousands of variables available!")
    print("Key variable groups:")
    print("  - B01xxx: Age and Sex")
    print("  - B08xxx: Income")
    print("  - B15xxx: Employment")
    print("  - B19xxx: Income")
    print("  - B25xxx: Education")
    print("  - B25xxx: Housing")
    print("\nFull variable list: https://api.census.gov/data/2023/acs/acs5/variables.html")
    
    # Test 3: Get some additional useful variables
    print("\n[3] ADDITIONAL USEFUL VARIABLES WE COULD ADD:")
    print("-" * 80)
    
    additional_variables = [
        'B25064_001E',    # Median Gross Rent
        'B25077_001E',    # Median Home Value
        'B15003_022E',    # Bachelor's Degree
        'B15003_023E',    # Master's Degree
        'B15003_024E',    # Professional Degree
        'B15003_025E',    # Doctorate Degree
        'B08301_021E',    # Public Transportation Commute
        'B08301_003E',    # Drove Alone Commute
        'B25003_002E',    # Owner-Occupied Housing
        'B25003_003E',    # Renter-Occupied Housing
        'B25001_001E',    # Total Housing Units
        'B25002_002E',    # Occupied Housing Units
        'B25002_003E',    # Vacant Housing Units
    ]
    
    url2 = f"{Config.CENSUS_API_BASE_URL}/{year}/{Config.CENSUS_DATASET}"
    params2 = {
        'get': ','.join(current_variables + additional_variables),
        'for': f'zip code tabulation area:{zip_code}',
        'key': Config.CENSUS_API_KEY if Config.CENSUS_API_KEY else ''
    }
    
    try:
        response2 = requests.get(url2, params=params2, timeout=30)
        if response2.status_code == 200:
            data2 = response2.json()
            if len(data2) > 1:
                headers2 = data2[0]
                row2 = data2[1]
                record2 = dict(zip(headers2, row2))
                
                print("Current + Additional Fields:")
                for key, value in record2.items():
                    if key in additional_variables:
                        print(f"  {key}: {value} (NEW)")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"Error: {response2.status_code}")
            print(response2.text[:500])
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("VARIABLE REFERENCE:")
    print("="*80)
    print("B01001_001E = Total Population")
    print("B01002_001E = Median Age")
    print("B19013_001E = Median Household Income")
    print("B19025_001E = Aggregate Household Income")
    print("B11001_001E = Total Households")
    print("B25064_001E = Median Gross Rent")
    print("B25077_001E = Median Home Value")
    print("B15003_022E = Bachelor's Degree (count)")
    print("B15003_023E = Master's Degree (count)")
    print("B25003_002E = Owner-Occupied Housing Units")
    print("B25003_003E = Renter-Occupied Housing Units")
    print("B25001_001E = Total Housing Units")
    print("\nFull documentation: https://api.census.gov/data/2023/acs/acs5/variables.html")

if __name__ == '__main__':
    # Test with a known zip code first (28204 - Charlotte)
    print("Testing with zip code 28204 (Charlotte, NC)...")
    test_census_api_fields('28204', '2022')
    print("\n\nNow testing with 20284...")
    test_census_api_fields('20284', '2022')
