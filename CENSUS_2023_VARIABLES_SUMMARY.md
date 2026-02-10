# Census 2023 ACS 5-Year Variables - Summary

**Total Variables:** 28,299

---

## Variables by Category

| Category | Count | Key Topics |
|----------|-------|------------|
| **Industry** | 6,344 | Occupation, industry, employment by sector |
| **Housing Characteristics** | 2,485 | Housing units, structure, bedrooms, utilities |
| **Demographics (B01-B09)** | 2,548 | Age, sex, race, mobility, place of birth |
| **Commuting (Journey to Work)** | 2,227 | Transportation mode, commute time, vehicles |
| **Occupancy** | 2,013 | Housing occupancy, vacancy, group quarters |
| **Poverty Status** | 1,965 | Poverty rates, income-to-poverty ratios |
| **Income** | 1,522 | Household income, income distribution, sources |
| **Earnings** | 1,092 | Individual earnings, work status, income by age |
| **Ancestry** | 892 | Citizenship, nativity, place of birth |
| **Language Spoken at Home** | 549 | Language use, English proficiency |
| **Employment Status** | 569 | Labor force, unemployment, employment by age |
| **Household/Family Type** | 405 | Family structure, household composition |
| **Age and Sex** | 359 | Age distribution, sex breakdowns |
| **Disability Status** | 374 | Disability rates, types of disabilities |
| **Educational Attainment** | 279 | Education levels, degrees, field of study |
| **Marital Status** | 458 | Marital status, divorce, widowhood |
| **Housing Costs** | 370 | Rent, mortgage, housing cost burden |
| **Fertility** | 199 | Birth rates, fertility by age |
| **Food Stamps/SNAP** | 121 | SNAP participation, food assistance |
| **Grandparents** | 186 | Grandparent caregivers |
| **Housing Value** | 213 | Home values, property values |
| **Housing Tenure** | 17 | Owner vs renter |
| **Hispanic Origin** | 55 | Hispanic/Latino ethnicity |
| **Other** | 448 | Data quality, allocation flags |

---

## Most Useful Variables for Real Estate Analysis

### Demographics
- **B01001_001E** - Total Population
- **B01002_001E** - Median Age
- **B01001_002E** - Male Population
- **B01001_026E** - Female Population
- **B01001_003E** - Under 5 Years
- **B01001_020E** - 65 Years and Over

### Income & Economics
- **B19013_001E** - Median Household Income
- **B19025_001E** - Aggregate Household Income
- **B19301_001E** - Per Capita Income
- **B19001_001E** - Household Income Distribution
- **B17001_001E** - Poverty Status

### Housing
- **B25001_001E** - Total Housing Units
- **B25002_002E** - Occupied Housing Units
- **B25002_003E** - Vacant Housing Units
- **B25003_002E** - Owner-Occupied Units
- **B25003_003E** - Renter-Occupied Units
- **B25077_001E** - Median Home Value
- **B25064_001E** - Median Gross Rent
- **B25031_001E** - Median Gross Rent (by income)

### Education
- **B15003_001E** - Total Population 25+
- **B15003_022E** - Bachelor's Degree
- **B15003_023E** - Master's Degree
- **B15003_024E** - Professional Degree
- **B15003_025E** - Doctorate Degree

### Commuting
- **B08301_001E** - Total Workers 16+
- **B08301_003E** - Drove Alone
- **B08301_004E** - Carpooled
- **B08301_010E** - Worked from Home
- **B08301_021E** - Public Transportation

### Employment
- **B23025_001E** - Total Population 16+
- **B23025_002E** - In Labor Force
- **B23025_005E** - Unemployed

---

## Variable Naming Convention

- **B** = Base table (estimate)
- **C** = Comparison table
- **S** = Subject table
- **DP** = Data Profile
- **CP** = Comparison Profile

**Suffixes:**
- **E** = Estimate
- **M** = Margin of Error
- **A-I** = Race/ethnicity breakdowns (A=White, B=Black, C=AIAN, D=Asian, E=NHOPI, F=Other, G=Two+, H=White Non-Hispanic, I=Hispanic)

**Examples:**
- `B01001_001E` = Base table B01001, variable 001, Estimate
- `B19013_001M` = Base table B19013, variable 001, Margin of Error
- `B01001B_001E` = Base table B01001, Black race, variable 001, Estimate

---

## How to Browse All Variables

**Census API Variable Explorer:**
- **2023 Variables:** https://api.census.gov/data/2023/acs/acs5/variables.html
- **Search by concept:** Use browser search (Ctrl+F) to find specific topics

**Variable Groups:**
- **B01xxx-B09xxx:** Demographics
- **B10xxx-B19xxx:** Social Characteristics
- **B20xxx-B29xxx:** Economic Characteristics
- **B25xxx:** Housing (largest category)

---

## Complete Variable List

A detailed markdown file with all 28,299 variables organized by category has been created:
**`CENSUS_2023_ALL_VARIABLES.md`**

This file contains:
- All variables organized by category
- Variable codes and labels
- Grouped by concept for easier browsing

---

## Quick Reference: Current vs Available

### Currently Using (6 variables):
1. B01001_001E - Total Population
2. B01002_001E - Median Age
3. B19013_001E - Median Household Income
4. B19025_001E - Aggregate Household Income
5. B11001_001E - Total Households
6. NAME - Geographic Name

### Recommended Additions:
- **B25077_001E** - Median Home Value
- **B25064_001E** - Median Gross Rent
- **B25003_002E** - Owner-Occupied Units
- **B25003_003E** - Renter-Occupied Units
- **B15003_022E-025E** - Education Levels
- **B08301_003E, B08301_021E** - Commute Methods

---

## Notes

- Variables ending in **M** are Margin of Error (not estimates)
- Variables with letter suffixes (A-I) are race/ethnicity breakdowns
- Some variables may return null/zero for small geographic areas
- All variables are available for ZCTA (zip code) level geography
