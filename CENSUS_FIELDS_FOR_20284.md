# Census Fields Available for Zip Code 20284 (2022/2023 Data)

## Current Fields We Fetch (6 fields):

| Field | Code | Example Value (28204) | Description |
|-------|------|----------------------|-------------|
| **Geographic Name** | `NAME` | "ZCTA5 28204" | ZCTA identifier |
| **Total Population** | `B01001_001E` | 9,525 | Total population count |
| **Median Age** | `B01002_001E` | 30.4 | Median age in years |
| **Median Household Income** | `B19013_001E` | $77,279 | Median income |
| **Aggregate Household Income** | `B19025_001E` | $675,352,100 | Total income (for calculating average) |
| **Total Households** | `B11001_001E` | 5,583 | Number of households |
| **Zip Code** | `zip code tabulation area` | "28204" | ZCTA code |

**Calculated Field:**
- **Average Household Income (AHHI)** = Aggregate Income ÷ Total Households = $120,978

---

## Additional Fields Available (Tested & Working):

### Housing & Real Estate (High Value for Real Estate):

| Field | Code | Example Value (28204) | Description |
|-------|------|----------------------|-------------|
| **Median Gross Rent** | `B25064_001E` | $1,559/month | Median monthly rent |
| **Median Home Value** | `B25077_001E` | $496,700 | Median home value |
| **Total Housing Units** | `B25001_001E` | 6,275 | Total housing units |
| **Occupied Housing Units** | `B25002_002E` | 5,583 | Occupied units |
| **Vacant Housing Units** | `B25002_003E` | 692 | Vacant units |
| **Owner-Occupied Units** | `B25003_002E` | 1,442 | Owner-occupied housing |
| **Renter-Occupied Units** | `B25003_003E` | 4,141 | Renter-occupied housing |

**Calculated Metrics:**
- **Homeownership Rate** = Owner-Occupied ÷ Occupied = 25.8%
- **Rental Rate** = Renter-Occupied ÷ Occupied = 74.2%
- **Vacancy Rate** = Vacant ÷ Total Units = 11.0%

### Education (Demographics):

| Field | Code | Example Value (28204) | Description |
|-------|------|----------------------|-------------|
| **Bachelor's Degree** | `B15003_022E` | 3,293 | Count with bachelor's |
| **Master's Degree** | `B15003_023E` | 1,275 | Count with master's |
| **Professional Degree** | `B15003_024E` | 745 | Count with professional |
| **Doctorate Degree** | `B15003_025E` | 162 | Count with doctorate |

**Note:** Need `B15003_001E` (Total Population 25+) to calculate percentages.

### Commute & Transportation:

| Field | Code | Example Value (28204) | Description |
|-------|------|----------------------|-------------|
| **Public Transportation** | `B08301_021E` | 1,746 | Commute by public transit |
| **Drove Alone** | `B08301_003E` | 3,717 | Commute by car alone |
| **Carpooled** | `B08301_004E` | (available) | Commute by carpool |
| **Worked from Home** | `B08301_010E` | (available) | Remote work |

---

## Complete Field Export Example for 20284

### If We Export All Available Fields:

**Demographics:**
- Zip Code: 20284
- State: [from geography]
- County: [from geography]
- Population: [value]
- Median Age: [value]
- Average Household Income (AHHI): [calculated]
- Median Household Income: [value]

**Housing (NEW):**
- Median Home Value: [value]
- Median Gross Rent: [value]
- Total Housing Units: [value]
- Owner-Occupied Units: [value]
- Renter-Occupied Units: [value]
- Occupied Units: [value]
- Vacant Units: [value]
- Homeownership Rate: [calculated %]
- Rental Rate: [calculated %]

**Education (NEW):**
- Bachelor's Degree Count: [value]
- Master's Degree Count: [value]
- Professional Degree Count: [value]
- Doctorate Count: [value]
- Education Level %: [calculated]

**Commute (NEW):**
- Public Transit Commuters: [value]
- Drive Alone Commuters: [value]
- Carpool Commuters: [value]
- Remote Workers: [value]

---

## Note on Zip Code 20284

**Status:** Returned 204 (No Content) from Census API

**Possible Reasons:**
1. Zip code might not exist or be too small
2. Data might not be available for this ZCTA
3. Might be a PO Box only zip code (no residential data)

**Recommendation:** Test with a different zip code that has data (like 28204 which worked).

---

## Recommended Fields to Add

### Priority 1 (Real Estate Focus):
1. ✅ **Median Home Value** (`B25077_001E`) - Critical for property analysis
2. ✅ **Median Gross Rent** (`B25064_001E`) - Critical for rental market
3. ✅ **Owner vs Renter** (`B25003_002E`, `B25003_003E`) - Housing tenure
4. ✅ **Total Housing Units** (`B25001_001E`) - Market size

### Priority 2 (Demographics):
5. ✅ **Education Levels** (`B15003_022E-025E`) - Education demographics
6. **Commute Methods** (`B08301_003E`, `B08301_021E`) - Transportation

### Priority 3 (Optional):
7. **Age Distribution** - More detailed demographics
8. **Poverty Status** - Economic health indicators

---

## How to See All Available Fields

**Census API Variable Explorer:**
- **2022:** https://api.census.gov/data/2022/acs/acs5/variables.html
- **2023:** https://api.census.gov/data/2023/acs/acs5/variables.html

**Search by topic:**
- Housing: Search "B25"
- Education: Search "B15"
- Income: Search "B19"
- Commute: Search "B08"

---

## Next Steps

1. **Choose which fields you want** - Review the list above
2. **Update database schema** - Add columns for new fields
3. **Update Census API client** - Add variables to fetch
4. **Re-fetch data** - Populate new fields

Would you like me to add specific fields to the system?
