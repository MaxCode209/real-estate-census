# Census Data Completeness & Updates

## Current Issues

### 1. State & County Columns Are Blank ❌

**Why:**
- The Census API call is **not requesting state/county data**
- Only fetching: zip_code, population, median_age, average_household_income
- State and county fields exist in the database but aren't being populated

**Current Code Issue:**
```python
# In backend/census_api.py - fetch_zip_code_data()
# Only requests these variables:
variables = [
    'NAME',           # Geographic name
    'B01001_001E',    # Total Population
    'B01002_001E',    # Median Age
    'B19013_001E',    # Median Household Income
    'B19025_001E',    # Aggregate Household Income
    'B11001_001E',    # Total Households
]
# Missing: State and County geography!
```

**Solution:** Need to add state/county to the API request using Census geography parameters.

---

## 2. Official Dataset Name

**Current Dataset:** 
- **Name:** American Community Survey 5-Year Estimates
- **API Path:** `acs/acs5`
- **Full URL:** `https://api.census.gov/data/2022/acs/acs5`
- **Official Name:** ACS 5-Year Data Profiles

**What It Is:**
- **ACS (American Community Survey)** - Ongoing survey by US Census Bureau
- **5-Year Estimates** - Combines 5 years of data for more reliable estimates
- **Coverage:** All geographic areas, including small zip codes
- **Release Schedule:** Annual (new data each year)

**Official Documentation:**
- **Census API Explorer:** https://api.census.gov/data.html
- **ACS Data:** https://www.census.gov/data/developers/data-sets/acs-5year.html
- **Variable List:** https://api.census.gov/data/2022/acs/acs5/variables.html

---

## 3. Data Year: 2022 - Is This Current?

### Current Status:
- **Using:** 2022 ACS 5-Year Estimates
- **Latest Available:** Check Census Bureau website (typically 1-2 years behind current year)
- **2024 Status:** 2022 is likely the latest 5-year estimates available

### Census Release Schedule:
- **ACS 5-Year Estimates:** Released annually, typically in December
- **Coverage:** Data from 5 years prior (e.g., 2022 release covers 2018-2022)
- **Latest Release:** Check https://www.census.gov/programs-surveys/acs/data.html

### How to Update When New Data Releases:

**Option 1: Update Config (Recommended)**
```python
# In config/config.py
CENSUS_YEAR = '2023'  # Update when new data releases
```

**Option 2: Keep Multiple Years**
- Store data with `data_year` field
- Query by year: `WHERE data_year = '2022'` or `WHERE data_year = '2023'`
- Allows comparison across years

**Option 3: Automatic Year Detection**
- Could add logic to detect latest available year
- Query Census API metadata for available years

---

## Solutions

### Solution 1: Add State & County to Census API Request

**How Census Geography Works:**
- ZCTAs (Zip Code Tabulation Areas) can span multiple states/counties
- Need to request state/county as **geography parameters**, not variables
- Use `in` parameter to nest geography (e.g., `in=state:*`)

**Updated API Call:**
```python
# Request state and county along with zip code
geography = 'zip code tabulation area:*'
# Add state and county using 'in' parameter
# Format: 'in=state:*' or 'in=state:37' (for NC)
```

**Challenge:** 
- ZCTAs can cross county/state boundaries
- May need to handle multiple states/counties per zip code
- Or use primary state/county (most common)

### Solution 2: Use Zip Code to State/County Mapping

**Alternative Approach:**
- Use a zip code lookup table/service
- Map zip codes to primary state/county
- More reliable than Census geography (which can be complex)

**Sources:**
- USPS Zip Code Database
- Census ZCTA to County Relationship File
- Commercial zip code databases

---

## Recommended Implementation

### Step 1: Add State/County to Census API Request

Update `backend/census_api.py` to request state/county:

```python
def fetch_zip_code_data(self, zip_codes: Optional[List[str]] = None) -> List[Dict]:
    # Add state and county to geography
    if zip_codes:
        geography = f"zip code tabulation area:{','.join(zip_codes)}"
        # Request with state/county
        geography_params = f"{geography}&in=state:*"
    else:
        geography_params = 'zip code tabulation area:*&in=state:*'
    
    # Add state and county to variables (they come as geography fields)
    # Note: State/county come from geography, not variables
```

**Note:** Census API returns state/county codes in the response when using `in=state:*` parameter.

### Step 2: Parse State/County from Response

```python
# Census API returns state as FIPS code (e.g., "37" for NC)
# County as FIPS code (e.g., "119" for Mecklenburg County)
# Need to map FIPS codes to names

state_fips = record.get('state', '')
county_fips = record.get('county', '')

# Map FIPS to names (need lookup table or API)
state_name = fips_to_state.get(state_fips, '')
county_name = fips_to_county.get(f"{state_fips}{county_fips}", '')
```

### Step 3: Update Data Year When Available

**When 2023 data releases:**
1. Update `config/config.py`: `CENSUS_YEAR = '2023'`
2. Re-fetch data: `python scripts/fetch_census_data.py`
3. New records will have `data_year = '2023'`
4. Old records keep `data_year = '2022'`

**Or keep both years:**
- Store multiple years in database
- Query by year as needed
- Compare trends across years

---

## Next Steps

1. ✅ **Add state/county fetching** to Census API client
2. ✅ **Create FIPS code lookup** for state/county names
3. ✅ **Update fetch logic** to populate state/county fields
4. ⏸️ **Monitor for 2023 data** release (check Census website)
5. ⏸️ **Update year** when new data available

---

## Resources

- **Census API Documentation:** https://www.census.gov/data/developers/data-sets/acs-5year.html
- **ACS Release Schedule:** https://www.census.gov/programs-surveys/acs/data.html
- **FIPS Code Lookup:** https://www.census.gov/library/reference/code-lists/ansi.html
- **ZCTA Documentation:** https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html
