# Answers to Census Data Questions

## 1. Why Are State & County Columns Blank?

### The Problem:
- ✅ Database has `state` and `county` columns
- ❌ Census API code **doesn't request** state/county data
- ❌ Only fetching: zip_code, population, median_age, average_household_income

### Why This Happened:
The Census API requires **special geography parameters** to get state/county:
- State/county come from **geography**, not variables
- Need to use `in=state:*` parameter in API call
- ZCTAs can span multiple counties, so need to handle that

### Solution Implemented:
✅ **Updated `backend/census_api.py`** to:
- Add `in=state:*` parameter to API requests
- Extract state FIPS code from response
- Convert FIPS to state code (e.g., "37" → "NC")
- Extract county FIPS code (county name lookup can be added later)

### To Populate Existing Data:
Run this script to backfill state/county for existing records:
```bash
python scripts/add_state_county_to_census.py
```

---

## 2. Official Dataset Name

### Current Dataset:
- **Full Name:** American Community Survey 5-Year Estimates
- **API Path:** `acs/acs5`
- **Full URL:** `https://api.census.gov/data/2022/acs/acs5`
- **Official Name:** ACS 5-Year Data Profiles

### What It Is:
- **ACS (American Community Survey)** - Ongoing demographic survey by US Census Bureau
- **5-Year Estimates** - Combines 5 years of data (e.g., 2018-2022) for reliability
- **Coverage:** All geographic areas including small zip codes
- **Release Schedule:** Annual (new data each December)

### Official Documentation:
- **Census API Explorer:** https://api.census.gov/data.html
- **ACS 5-Year Data:** https://www.census.gov/data/developers/data-sets/acs-5year.html
- **Variable List:** https://api.census.gov/data/2022/acs/acs5/variables.html

---

## 3. Data Year: 2022 - Is This Current?

### Current Status:
- **Using:** 2022 ACS 5-Year Estimates (covers 2018-2022)
- **Latest Available:** 2019-2023 (released in 2024)
- **Next Release:** 2020-2024 estimates (scheduled for January 29, 2026)

### Census Release Schedule:
- **ACS 5-Year Estimates:** Released annually in December
- **Coverage Period:** Data from 5 years prior (e.g., 2022 release = 2018-2022 data)
- **Latest Release:** Check https://www.census.gov/programs-surveys/acs/data.html

### Update Status:
- ✅ **2022 is NOT the latest** - 2019-2023 is available
- ⚠️ **2020-2024 will release Jan 29, 2026** (very soon!)

---

## 4. What Happens When New Data Releases?

### Option 1: Update Year (Recommended)
**When 2020-2024 data releases (Jan 29, 2026):**

1. **Update config:**
   ```python
   # In config/config.py
   CENSUS_YEAR = '2024'  # Update to latest year
   ```

2. **Re-fetch data:**
   ```bash
   python scripts/fetch_census_data.py
   ```

3. **Result:**
   - New records get `data_year = '2024'`
   - Old records keep `data_year = '2022'`
   - Both years coexist in database

### Option 2: Keep Multiple Years (Advanced)
**Store data from multiple years:**

- Allows comparison: "How did population change from 2022 to 2024?"
- Query by year: `WHERE data_year = '2022'` or `WHERE data_year = '2024'`
- Track trends over time

### Option 3: Replace Old Data
**Overwrite existing records:**

- Update existing zip codes with new year data
- Simpler, but lose historical data
- Good if you only need latest data

---

## Recommended Next Steps

### Immediate Actions:

1. ✅ **Update Census API** - Already done! Now fetches state/county
2. ✅ **Backfill State/County** - Run script to populate existing records
3. ⏸️ **Update to 2023 Data** - Change `CENSUS_YEAR = '2023'` in config
4. ⏸️ **Monitor for 2024 Release** - Check Jan 29, 2026 for new data

### To Update to Latest Year (2023):

1. **Update config:**
   ```python
   # config/config.py
   CENSUS_YEAR = '2023'  # Latest available 5-year estimates
   ```

2. **Re-fetch data:**
   ```bash
   python scripts/fetch_census_data.py
   ```

3. **Verify:**
   ```sql
   -- In Supabase SQL Editor
   SELECT data_year, COUNT(*) 
   FROM census_data 
   GROUP BY data_year;
   ```

---

## Summary

### State/County Issue:
- ✅ **Fixed:** Code now requests state/county from Census API
- ✅ **State:** Will be populated (FIPS → state code conversion)
- ⚠️ **County:** FIPS code extracted, name lookup can be added later

### Dataset Name:
- **Official:** American Community Survey 5-Year Estimates (ACS 5-Year)
- **API Path:** `acs/acs5`
- **Source:** US Census Bureau

### Data Year:
- **Current:** 2022 (2018-2022 data)
- **Latest Available:** 2023 (2019-2023 data)
- **Next Release:** 2024 (2020-2024 data) - Jan 29, 2026

### Updates:
- **When new data releases:** Update `CENSUS_YEAR` in config and re-fetch
- **Can keep multiple years:** Store both 2022 and 2023 data
- **Automatic:** No manual intervention needed, just update config
