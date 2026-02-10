# City Column — How to Add and Populate

This guide covers adding a **city** column to `census_data` and assigning a city to each zip code so you can later add "Search by City" (or other city-based functionality) as you prefer.

**No zip→city CSV?** Use **Option C** below: a script that fetches city from the free Zippopotam.us API for every zip in your database and caches results so you only pay the API cost once.

---

## 1. Add the column to the database

**Recommended (Supabase):** Run the SQL in the **Supabase SQL Editor** so the ALTER doesn’t hit the pooler’s statement timeout.

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your project → **SQL Editor**.
2. Paste and run:

```sql
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;
CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
```

Or run the file: `scripts/supabase_add_city_column.sql`

**Alternative (from your machine):** Run the Python migration (can hit statement timeout on Supabase pooler):

```bash
python scripts/migrate_add_city_to_census.py
```

- Safe to run more than once (skips if column already exists).
- If you see `statement timeout`, use the SQL Editor method above.

---

## 2. Assign cities to zip codes

### Option A: Export → Edit CSV → Import (recommended)

1. **Export** all zip codes (and current city if any) to a CSV:
   ```bash
   python scripts/export_zips_for_city.py
   ```
   Creates: `data/zip_codes_for_city.csv` with columns `zip_code`, `city`.

2. **Edit the CSV** (Excel, Google Sheets, etc.):
   - Fill in the **city** column for each zip (e.g. "Charlotte", "Raleigh", "Myrtle Beach").
   - One zip can have one city; one city can appear on many rows (many zips).

3. **Update the database** from the CSV:
   ```bash
   python scripts/assign_city_from_csv.py
   ```
   Or with a custom path:
   ```bash
   python scripts/assign_city_from_csv.py path/to/your_zip_city.csv
   ```

### Option B: Use your own CSV

If you already have a file with `zip_code` and `city` columns:

```bash
python scripts/assign_city_from_csv.py path/to/zip_city.csv
```

The script updates `census_data.city` for each zip that exists in your table; rows not in the DB are skipped.

### Option C: Fetch city from Zippopotam.us API (no CSV needed)

If you don’t have a zip→city CSV, you can populate `city` using the free **Zippopotam.us** API (no API key):

1. **Run the migration** (if you haven’t):
   ```bash
   python scripts/migrate_add_city_to_census.py
   ```

2. **Fetch city for every zip** in your database:
   ```bash
   python scripts/fetch_city_for_zips.py
   ```
   - For each zip in `census_data`, the script calls `https://api.zippopotam.us/us/{zip}` and sets `city` from the returned “place name”.
   - Results are cached in **`data/zip_to_city_cache.json`**, so re-runs only call the API for zips not yet in the cache.
   - Default delay between requests is 0.25 seconds (use `--delay 0.5` if you want to be gentler).

3. **Optional flags:**
   - **Test on a few zips:** `python scripts/fetch_city_for_zips.py --limit 50`
   - **Only build cache, don’t update DB:** `python scripts/fetch_city_for_zips.py --dry-run`
   - **Slower rate:** `python scripts/fetch_city_for_zips.py --delay 0.5`

For a few thousand zips, a full run can take on the order of 10–20 minutes once; after that, the cache makes re-runs or new zips fast.

---

## 3. Model and API

- **Model:** `CensusData` in `backend/models.py` now has `city = Column(String(100), nullable=True, index=True)` and includes `city` in `to_dict()`.
- **Filtering:** Once cities are assigned, you can add an API filter, e.g. `GET /api/census-data?city=Charlotte`, and use it in the UI for "Search by City" and highlighting all zips in that city (that part is not implemented yet; this guide only covers the column and population).

---

## 4. Order of operations

1. Run **migrate_add_city_to_census.py** (add column).
2. Run **export_zips_for_city.py** (optional; only if you want to fill city in a spreadsheet).
3. Fill in the **city** column in the CSV (or use your own zip→city file).
4. Run **assign_city_from_csv.py** to update the database.

After that, `census_data` has a populated `city` column and you can add the "Search by City" UI and map highlighting when you’re ready.
