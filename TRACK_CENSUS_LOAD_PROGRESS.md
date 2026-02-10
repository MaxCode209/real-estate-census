# How to Track Census 2024 Load Progress in Supabase

Use these in the **Supabase SQL Editor** (Dashboard → SQL Editor) to see progress and confirm the load is working.

---

## 1. Progress: How Many Rows Updated So Far

**Updated count (2024 data + new fields):**

```sql
-- Rows that have been updated with 2024 data
-- (data_year = '2024' and population is set)
SELECT 
  COUNT(*) AS rows_with_2024_data,
  COUNT(CASE WHEN total_households IS NOT NULL THEN 1 END) AS with_total_households,
  COUNT(CASE WHEN owner_occupied_units IS NOT NULL THEN 1 END) AS with_owner_occupied,
  COUNT(CASE WHEN renter_occupied_units IS NOT NULL THEN 1 END) AS with_renter_occupied,
  COUNT(CASE WHEN net_migration_yoy IS NOT NULL THEN 1 END) AS with_net_migration_yoy
FROM census_data
WHERE data_year = '2024' AND population IS NOT NULL;
```

Run this periodically; **rows_with_2024_data** should increase as the script runs.

---

## 2. Progress: Share Done vs Total

**Rough % complete:**

```sql
-- Total zip codes and how many have 2024 data so far
SELECT 
  (SELECT COUNT(DISTINCT zip_code) FROM census_data) AS total_zips,
  (SELECT COUNT(*) FROM census_data WHERE data_year = '2024' AND population IS NOT NULL) AS updated_so_far,
  ROUND(
    100.0 * (SELECT COUNT(*) FROM census_data WHERE data_year = '2024' AND population IS NOT NULL) 
    / NULLIF((SELECT COUNT(DISTINCT zip_code) FROM census_data), 0),
    2
  ) AS pct_complete;
```

**pct_complete** is your progress percentage.

---

## 3. Recent Updates (Confirm It’s Moving)

**Last-updated rows:**

```sql
-- Rows updated most recently (script writes in batches)
SELECT 
  zip_code,
  state,
  population,
  median_age,
  average_household_income,
  total_households,
  owner_occupied_units,
  renter_occupied_units,
  net_migration_yoy,
  data_year,
  updated_at
FROM census_data
WHERE data_year = '2024' AND population IS NOT NULL
ORDER BY updated_at DESC
LIMIT 20;
```

If **updated_at** values are recent and keep changing as you re-run, the load is actively writing.

---

## 4. Sanity Check: New Fields Look Right

**Spot-check a few zips:**

```sql
-- Sample of 2024 rows with all new fields
SELECT 
  zip_code,
  state,
  county,
  population,
  median_age,
  average_household_income,
  total_households,
  owner_occupied_units,
  renter_occupied_units,
  moved_from_different_state,
  moved_from_different_county,
  moved_from_abroad,
  net_migration_yoy,
  data_year
FROM census_data
WHERE data_year = '2024' 
  AND population IS NOT NULL 
  AND total_households IS NOT NULL
ORDER BY updated_at DESC
LIMIT 10;
```

Check that:
- **population**, **median_age**, **average_household_income** are non-null and plausible.
- **total_households**, **owner_occupied_units**, **renter_occupied_units** are non-null where you expect them.
- **net_migration_yoy** is a small number (e.g. -5 to +10) when present; null is ok if there was no 2023 row.

---

## 5. Quick “Is It Working?” One-Liner

**Single progress number:**

```sql
SELECT COUNT(*) AS "2024 rows updated"
FROM census_data
WHERE data_year = '2024' AND population IS NOT NULL;
```

As the script runs, this count should go up. When the script finishes, it should be close to your total number of zip codes (~33,774 if you used `--from-db`).

---

## 6. After the Load: Year and Net Migration Summary

**When the run is done:**

```sql
SELECT 
  data_year,
  COUNT(*) AS rows,
  COUNT(net_migration_yoy) AS with_net_migration,
  ROUND(AVG(net_migration_yoy)::numeric, 2) AS avg_net_migration_pct
FROM census_data
GROUP BY data_year
ORDER BY data_year;
```

You should see:
- **data_year = '2024'** with most of your rows.
- **with_net_migration** ≈ number of zips that had 2023 data.
- **avg_net_migration_pct** a small number (e.g. -2 to +5).

---

## 7. Where to Run These

1. Open **Supabase Dashboard**: https://supabase.com/dashboard  
2. Select your project.  
3. Left sidebar → **SQL Editor**.  
4. Paste a query, click **Run**.

No need to refresh the Table Editor; re-running the query is enough to see new progress.

---

## How You Know It’s Working

- **Terminal:** You see batch lines like  
  `Batch 5: fetched 50 records (250 total)`  
  and at the end  
  `Stored 0 new records and updated N existing records`  
  with N growing.
- **Supabase:** The “2024 rows updated” count (query in section 5) goes up over time and matches the terminal’s updated count when the run finishes.
- **Sanity:** A few rows from the query in section 4 have sensible numbers and recent **updated_at** times.

If the terminal shows batches but the Supabase count doesn’t increase, the script might be talking to a different database (e.g. local vs Supabase). Check that `DATABASE_URL` in your `.env` points at your Supabase project.
