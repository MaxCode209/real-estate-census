"""Example usage of the API endpoints."""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def example_get_all_data():
    """Example: Get all census data."""
    response = requests.get(f'{BASE_URL}/census-data')
    data = response.json()
    print(f"Total records: {data['total']}")
    print(f"First record: {json.dumps(data['data'][0], indent=2) if data['data'] else 'No data'}")

def example_get_by_zip(zip_code):
    """Example: Get data for specific zip code."""
    response = requests.get(f'{BASE_URL}/census-data/zip/{zip_code}')
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.json()}")

def example_filter_data():
    """Example: Filter data by income and population."""
    params = {
        'min_income': 50000,
        'max_income': 100000,
        'min_population': 10000,
        'limit': 10
    }
    response = requests.get(f'{BASE_URL}/census-data', params=params)
    data = response.json()
    print(f"Found {data['total']} records matching criteria")
    for record in data['data'][:5]:
        print(f"Zip {record['zip_code']}: ${record['average_household_income']:,.0f} income, {record['population']:,} population")

def example_add_data():
    """Example: Add or update census data."""
    new_data = {
        'zip_code': '10001',
        'state': 'NY',
        'population': 50000,
        'median_age': 35.5,
        'average_household_income': 75000,
        'data_year': '2022'
    }
    response = requests.post(f'{BASE_URL}/census-data', json=new_data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def example_bulk_add():
    """Example: Bulk add multiple records."""
    bulk_data = [
        {
            'zip_code': '10002',
            'population': 45000,
            'median_age': 32.0,
            'average_household_income': 65000,
            'data_year': '2022'
        },
        {
            'zip_code': '10003',
            'population': 48000,
            'median_age': 34.0,
            'average_household_income': 70000,
            'data_year': '2022'
        }
    ]
    response = requests.post(f'{BASE_URL}/census-data/bulk', json=bulk_data)
    print(json.dumps(response.json(), indent=2))

def example_fetch_from_census():
    """Example: Fetch data from Census API and store."""
    # Fetch specific zip codes
    response = requests.post(
        f'{BASE_URL}/census-data/fetch',
        json={'zip_codes': ['10001', '10002', '10003']}
    )
    print(json.dumps(response.json(), indent=2))

def example_export_to_sheets():
    """Example: Export data to Google Sheets."""
    response = requests.get(f'{BASE_URL}/export/sheets')
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    print("API Usage Examples\n" + "="*50)
    
    # Uncomment the examples you want to run:
    
    # example_get_all_data()
    # example_get_by_zip('10001')
    # example_filter_data()
    # example_add_data()
    # example_bulk_add()
    # example_fetch_from_census()
    # example_export_to_sheets()

