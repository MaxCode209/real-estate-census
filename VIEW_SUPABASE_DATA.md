# How to View Your Database in Supabase

To inspect schema (columns) from the repo and share with the app: run  
`python scripts/describe_census_schema.py` and paste the output.  
For how we change schema and avoid timeouts, see **SUPABASE_WORKFLOW.md**.

## Quick Access

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project** (the one we set up earlier)
3. **Click "Table Editor"** in the left sidebar
4. **Click on `census_data` table**

You'll see all your census data in a spreadsheet-like view!

## What You'll See

The `census_data` table contains:
- `zip_code` - The zip code
- `population` - Total population
- `median_age` - Median age
- `average_household_income` - Median Household Income from Census (B19013_001E); label in app as "MHI"
- `data_year` - Year of the data
- `created_at` - When it was added
- `updated_at` - When it was last updated

## Alternative: Use SQL Editor

1. In Supabase dashboard, click **"SQL Editor"** in left sidebar
2. Run this query to see all your data:

```sql
SELECT 
  zip_code,
  population,
  median_age,
  average_household_income,
  data_year
FROM census_data
ORDER BY zip_code
LIMIT 100;
```

## Export to CSV/Excel

1. In Table Editor, click the **"..."** menu (top right)
2. Select **"Export as CSV"** or use the download button
3. Open in Excel/Sheets

## Tracking Census 2024 Load Progress

While `python scripts/fetch_census_data.py --from-db` is running, use the queries in **`TRACK_CENSUS_LOAD_PROGRESS.md`** to see how many rows have 2024 data and confirm it's working.

Quick progress check in SQL Editor:

```sql
SELECT COUNT(*) AS "2024 rows updated"
FROM census_data
WHERE data_year = '2024' AND population IS NOT NULL;
```

That number should increase as the script runs.

---

## Quick Stats Query

To see summary statistics:

```sql
SELECT 
  COUNT(*) as total_records,
  AVG(population) as avg_population,
  AVG(average_household_income) as avg_income,
  AVG(median_age) as avg_age
FROM census_data;
```
