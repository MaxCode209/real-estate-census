# Available Census Fields - Complete Reference

## Testing Zip Code: 20284

### Current Fields We Fetch (2022 Data):

| Field Code | Field Name | Description | Example Value |
|------------|------------|-------------|---------------|
| `NAME` | Geographic Name | ZCTA name | "ZCTA5 20284" |
| `B01001_001E` | Total Population | Total population count | 15,234 |
| `B01002_001E` | Median Age | Median age of residents | 38.5 |
| `B19013_001E` | Median Household Income | Median household income | 65,432 |
| `B19025_001E` | Aggregate Household Income | Total income (for calculating average) | 1,234,567,890 |
| `B11001_001E` | Total Households | Number of households | 5,678 |
| `state` | State FIPS Code | State code (when using `in=state:*`) | "37" (NC) |
| `county` | County FIPS Code | County code (when using `in=state:*`) | "119" (Mecklenburg) |
| `zip code tabulation area` | ZCTA Code | Zip code | "20284" |

---

## Additional Fields Available from Census API

### Housing & Real Estate Fields:

| Field Code | Field Name | Description | Use Case |
|------------|------------|-------------|----------|
| `B25064_001E` | Median Gross Rent | Median monthly rent | Rental market analysis |
| `B25077_001E` | Median Home Value | Median home value | Property value analysis |
| `B25001_001E` | Total Housing Units | Total housing units | Market size |
| `B25002_002E` | Occupied Housing Units | Occupied units | Occupancy rate |
| `B25002_003E` | Vacant Housing Units | Vacant units | Vacancy rate |
| `B25003_002E` | Owner-Occupied Housing | Owner-occupied units | Homeownership rate |
| `B25003_003E` | Renter-Occupied Housing | Renter-occupied units | Rental market size |
| `B25031_001E` | Median Gross Rent (by income) | Rent affordability | Affordability analysis |
| `B25075_001E` | Value Specified | Homes with value data | Data completeness |

### Education Fields:

| Field Code | Field Name | Description | Use Case |
|------------|------------|-------------|----------|
| `B15003_022E` | Bachelor's Degree | Count with bachelor's | Education level |
| `B15003_023E` | Master's Degree | Count with master's | Education level |
| `B15003_024E` | Professional Degree | Count with professional | Education level |
| `B15003_025E` | Doctorate Degree | Count with doctorate | Education level |
| `B15003_001E` | Total Population 25+ | Population 25 and older | Education denominator |
| `B15002_001E` | Educational Attainment | Overall education stats | Education profile |

### Employment & Commute:

| Field Code | Field Name | Description | Use Case |
|------------|------------|-------------|----------|
| `B08301_021E` | Public Transportation | Commute by public transit | Transportation |
| `B08301_003E` | Drove Alone | Commute by car alone | Transportation |
| `B08301_004E` | Carpooled | Commute by carpool | Transportation |
| `B08301_010E` | Worked from Home | Remote work | Work patterns |
| `B23025_002E` | In Labor Force | Labor force participation | Employment |
| `B23025_005E` | Unemployed | Unemployment count | Employment |

### Income & Poverty:

| Field Code | Field Name | Description | Use Case |
|------------|------------|-------------|----------|
| `B19001_001E` | Household Income Distribution | Income brackets | Income distribution |
| `B17001_001E` | Poverty Status | Poverty statistics | Economic health |
| `B19301_001E` | Per Capita Income | Income per person | Economic indicators |

### Age & Demographics:

| Field Code | Field Name | Description | Use Case |
|------------|------------|-------------|----------|
| `B01001_002E` | Male Population | Male count | Gender demographics |
| `B01001_026E` | Female Population | Female count | Gender demographics |
| `B01001_003E` | Under 5 Years | Young children | Age distribution |
| `B01001_020E` | 65 Years and Over | Senior population | Age distribution |

---

## Complete Field List Reference

**Census API Variable Explorer:**
- **2022 Variables:** https://api.census.gov/data/2022/acs/acs5/variables.html
- **2023 Variables:** https://api.census.gov/data/2023/acs/acs5/variables.html

**Variable Groups:**
- **B01xxx:** Age and Sex
- **B08xxx:** Commuting
- **B15xxx:** Education
- **B19xxx:** Income
- **B25xxx:** Housing
- **B17xxx:** Poverty
- **B23xxx:** Employment

---

## Recommended Additional Fields for Real Estate

### High Priority:
1. ✅ **Median Home Value** (`B25077_001E`) - Property values
2. ✅ **Median Gross Rent** (`B25064_001E`) - Rental market
3. ✅ **Owner vs Renter** (`B25003_002E`, `B25003_003E`) - Housing tenure
4. ✅ **Education Levels** (`B15003_022E-025E`) - Education demographics

### Medium Priority:
5. **Commute Methods** (`B08301_003E`, `B08301_021E`) - Transportation
6. **Housing Occupancy** (`B25002_002E`, `B25002_003E`) - Market health
7. **Per Capita Income** (`B19301_001E`) - Economic indicator

### Low Priority:
8. **Age Distribution** (`B01001_003E`, `B01001_020E`) - Demographics
9. **Poverty Status** (`B17001_001E`) - Economic health

---

## Example: What 20284 Would Look Like with All Fields

**Current Export (6 fields):**
- Zip Code, Population, Median Age, AHHI, State, County

**Enhanced Export (15+ fields):**
- Zip Code, Population, Median Age, AHHI, State, County
- **Plus:** Median Home Value, Median Rent, Owner %, Renter %, Education Levels, Commute Methods, etc.

---

## How to Add More Fields

1. **Update `backend/census_api.py`:**
   ```python
   variables = [
       'NAME',
       'B01001_001E',    # Population (current)
       'B01002_001E',    # Median Age (current)
       'B19013_001E',    # Median Income (current)
       'B19025_001E',    # Aggregate Income (current)
       'B11001_001E',    # Total Households (current)
       'B25077_001E',    # Median Home Value (NEW)
       'B25064_001E',    # Median Rent (NEW)
       'B25003_002E',    # Owner-Occupied (NEW)
       'B25003_003E',    # Renter-Occupied (NEW)
       # ... add more as needed
   ]
   ```

2. **Update `backend/models.py`:**
   ```python
   median_home_value = Column(Float, nullable=True)
   median_rent = Column(Float, nullable=True)
   owner_occupied_units = Column(Integer, nullable=True)
   renter_occupied_units = Column(Integer, nullable=True)
   ```

3. **Update database schema:**
   ```sql
   ALTER TABLE census_data ADD COLUMN median_home_value FLOAT;
   ALTER TABLE census_data ADD COLUMN median_rent FLOAT;
   -- etc.
   ```

---

## Next Steps

1. **Test current fields** - See what 20284 returns with 2022 data
2. **Choose additional fields** - Select which ones you want
3. **Update code** - Add fields to API call and database
4. **Re-fetch data** - Populate new fields for existing zip codes
