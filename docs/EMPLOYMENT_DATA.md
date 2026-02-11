## NC Top Employers Dataset

Source CSV: `c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Project Datasets\NC_Top_Employers_with_Salaries.csv`

Each row represents one employer that appears in the NC Department of Commerce “Top Employers” report for a given county. The raw headers and the normalization rules we will apply before loading to Supabase are:

| Raw Column | Normalized Field | Notes |
| --- | --- | --- |
| `Area Name` | `county_name` | Trim surrounding whitespace. Store title case as-provided (e.g., `Alamance County`). |
| `Year` | `year` (int) | Current file only contains `2024`. Parse as integer. |
| `Company Name` | `company_name` | Trim whitespace; preserve internal capitalization. |
| `Industry` | `industry` | Trim whitespace. |
| `Class` | `sector_class` enum | Values are either `Private Sector` or `Public Sector`. Store as lowercase snake case (`private_sector`, `public_sector`) for consistency. |
| `Employment Range` | `employment_range` enum | Valid values discovered: `Below 50`, `50-99`, `100-249`, `250-499`, `500-999`, `1000+`. Persist the exact label but trim whitespace for comparison. |
| `Rank` | `rank` (int) | Parse to integer. |
| `Avg Salary` | `avg_salary` (int) | Strip `$`, commas, spaces (e.g., `"$62,000 "` -> `62000`). Store `NULL` if the cleaned string is empty or non-numeric. |

### Geography normalization
* `state_code` will be stored as `NC`.
* `county_fips` is auto-populated by matching `county_name` against the local `data/nc_county_fips.csv` file (built from the Census “national_county” reference). Values are 5-digit strings (e.g., `37001` for Alamance).

### Employment scoring
Employment-based scores will be calculated later and stored on the `census_data` records. The `county_employers` table now focuses purely on employer metadata to keep imports simple.
