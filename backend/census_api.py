"""Client for interacting with US Census Bureau API."""
import time
import requests
from typing import Dict, List, Optional
from config.config import Config

class CensusAPIClient:
    """Client for fetching data from US Census Bureau API."""
    
    def __init__(self):
        self.base_url = Config.CENSUS_API_BASE_URL
        self.year = Config.CENSUS_YEAR
        self.dataset = Config.CENSUS_DATASET
        self.api_key = Config.CENSUS_API_KEY
    
    def _build_url(self, variables: List[str], geography: str = 'zip code tabulation area:*') -> str:
        """Build API URL with parameters."""
        # Census API variable codes:
        # B01001_001E: Total Population, B01002_001E: Median Age
        # B19013_001E: Median Household Income (official Census stat)
        # B11001_001E: Total Households, B25003_*: housing, B07001_*: mobility
        vars_str = ','.join(variables)
        url = f"{self.base_url}/{self.year}/{self.dataset}"
        params = {
            'get': vars_str,
            'for': geography,
            'key': self.api_key if self.api_key else ''
        }
        query_parts = [f"{k}={v}" for k, v in params.items() if v]
        return f"{url}?{'&'.join(query_parts)}"
    
    def fetch_zip_code_data(self, zip_codes: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch census data for zip codes.
        
        Args:
            zip_codes: List of zip codes to fetch. If None, fetches all.
        
        Returns:
            List of dictionaries with census data
        """
        # Census variable codes: B19013 = Median Household Income (official Census stat)
        variables = [
            'NAME',
            'B01001_001E',    # Total Population
            'B01002_001E',    # Median Age
            'B19013_001E',    # Median Household Income (Census official stat)
            'B11001_001E',    # Total Households
            'B25003_002E',    # Owner-Occupied Housing Units
            'B25003_003E',    # Renter-Occupied Housing Units
            'B07001_017E',    # Moved from Different State (past year)
            'B07001_033E',    # Moved from Different County, Same State (past year)
            'B07001_049E',    # Moved from Abroad (past year)
        ]
        
        if zip_codes:
            geography = f"zip code tabulation area:{','.join(zip_codes)}"
        else:
            geography = 'zip code tabulation area:*'
        
        url = self._build_url(variables, geography)
        max_retries = 4
        base_delay = 5
        
        try:
            for attempt in range(max_retries):
                response = requests.get(url, timeout=60)
                if response.ok:
                    break
                err_preview = (response.text or '')[:500]
                print(f"Census API error {response.status_code}: {err_preview}")
                if response.status_code in (503, 429) and attempt < max_retries - 1:
                    delay = base_delay * (3 ** attempt)
                    print(f"  Retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                    continue
                response.raise_for_status()
            
            if response.headers.get('Content-Type', '').startswith('text/html'):
                if self.api_key:
                    print(f"Warning: API key may be invalid. Trying without key...")
                    url_no_key = url.replace(f'&key={self.api_key}', '').replace(f'?key={self.api_key}&', '?').replace(f'?key={self.api_key}', '')
                    response = requests.get(url_no_key, timeout=30)
                    response.raise_for_status()
                else:
                    raise ValueError("Invalid API response (HTML instead of JSON)")
            
            data = response.json()
            if not data or len(data) < 2:
                return []
            
            headers = data[0]
            results = []
            for row in data[1:]:
                if len(row) != len(headers):
                    continue
                record = dict(zip(headers, row))
                zip_code = record.get('zip code tabulation area', '')
                if not zip_code:
                    continue
                try:
                    population = int(record.get('B01001_001E', 0) or 0)
                    total_households = int(record.get('B11001_001E', 0) or 0)
                    median_household_income = record.get('B19013_001E')
                    if median_household_income is not None and median_household_income != '':
                        median_household_income = float(median_household_income)
                    else:
                        median_household_income = None  # Census uses -666666666 for null/NA
                    if median_household_income is not None and median_household_income < 0:
                        median_household_income = None
                    median_age_raw = record.get('B01002_001E')
                    median_age = float(median_age_raw) if (median_age_raw is not None and median_age_raw != '' and float(median_age_raw) >= 0) else None
                    owner_occupied = int(record.get('B25003_002E', 0) or 0)
                    renter_occupied = int(record.get('B25003_003E', 0) or 0)
                    moved_from_state = int(record.get('B07001_017E', 0) or 0)
                    moved_from_county = int(record.get('B07001_033E', 0) or 0)
                    moved_from_abroad = int(record.get('B07001_049E', 0) or 0)
                    results.append({
                        'zip_code': zip_code,
                        'state': None,
                        'county': None,
                        'population': population if population else None,
                        'median_age': median_age,
                        'average_household_income': median_household_income,  # Census B19013 (Median HHI)
                        'total_households': total_households,
                        'owner_occupied_units': owner_occupied,
                        'renter_occupied_units': renter_occupied,
                        'moved_from_different_state': moved_from_state,
                        'moved_from_different_county': moved_from_county,
                        'moved_from_abroad': moved_from_abroad,
                        'net_migration_yoy': None,
                        'data_year': self.year,
                    })
                except (ValueError, TypeError):
                    continue
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error fetching census data: {e}")
            return []
    
    def fetch_state_list(self) -> List[str]:
        """Fetch list of all state FIPS codes."""
        return []
