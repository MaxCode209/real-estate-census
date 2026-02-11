"""
Legacy helper that attempted to backfill `state` on census_data.

The `state` column has since been removed, so this script is kept only for
historical reference.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData
from backend.census_api import CensusAPIClient
import requests
from config.config import Config

# FIPS code lookup (common states)
STATE_FIPS_TO_CODE = {
    '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO',
    '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI',
    '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY',
    '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
    '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
    '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH',
    '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD',
    '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
    '54': 'WV', '55': 'WI', '56': 'WY'
}

def get_state_county_for_zip(zip_code):
    """
    Get state and county for a zip code using Census API.
    Uses ZCTA to County Relationship File approach.
    """
    try:
        # Method 1: Use Census API with geography nesting
        # Request zip code data with state/county geography
        url = f"{Config.CENSUS_API_BASE_URL}/{Config.CENSUS_YEAR}/{Config.CENSUS_DATASET}"
        params = {
            'get': 'NAME',
            'for': f'zip code tabulation area:{zip_code}',
            'in': 'state:*',
            'key': Config.CENSUS_API_KEY if Config.CENSUS_API_KEY else ''
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                # First row is headers, second row is data
                headers = data[0]
                row = data[1]
                record = dict(zip(headers, row))
                
                state_fips = record.get('state', '')
                county_fips = record.get('county', '')
                
                # Convert FIPS to state code
                state_code = STATE_FIPS_TO_CODE.get(state_fips, '')
                
                # Get county name (would need county FIPS lookup table)
                # For now, return state code and county FIPS
                return state_code, county_fips
        
        return None, None
    except Exception as e:
        print(f"Error getting state/county for {zip_code}: {e}")
        return None, None

def update_census_data_with_state_county():
    """No-op placeholder since census_data.state has been dropped."""
    raise SystemExit("census_data.state column has been removed; this script is no longer applicable.")

if __name__ == '__main__':
    update_census_data_with_state_county()
