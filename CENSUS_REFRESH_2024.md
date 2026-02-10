# Census 2024 Refresh – No Migration Required

The app uses your **existing** `census_data` table. No DDL (no rename, no drop columns)—so no Supabase timeouts.

- **Column** `average_household_income` stays as-is; we store **Census Median HHI (B19013)** in it.
- **UI label** everywhere is **"Median Household Income (MHI)"**.
- **state** and **county** columns stay in the table (can be null); we don’t drop them to avoid long-running ALTERs.

---

## Refresh all 2024 census data

From the project root, run:

```bash
python scripts/fetch_census_data.py --from-db --refresh
```

This will:

- Re-fetch all zip codes in your DB from the Census API.
- Overwrite 2024 rows with: population, median_age, **Median HHI** (in `average_household_income`), total_households, owner/renter units, moved_from_* fields, data_year = 2024.
- Set **updated_at** on every updated row.
- Compute **net_migration_yoy** where 2023 population exists.

### Progress output

You’ll see lines like:

```
Using 33774 zip codes to re-fetch and overwrite 2024 data (Median HHI in average_household_income, complete columns).

Fetching 2024 census data for 33774 zip codes (batch size 50, ~676 batches).
...

  Batch 1/676: 50/33774 zips (0%) — added 0, updated 50
  Batch 2/676: 100/33774 zips (0%) — added 0, updated 50
  ...
  Batch 676/676: 33774/33774 zips (100%) — ...

Done. Stored 0 new records and updated 33774 existing records.
```

If the connection drops, run the same command again; it will overwrite again.

---

## Verify (optional)

```bash
python scripts/verify_census_data.py --backfill
```

Reports null counts per column and lists zip codes missing any required field.

---

## Summary

| Step   | Command |
|--------|---------|
| Refresh | `python scripts/fetch_census_data.py --from-db --refresh` |
| Verify  | `python scripts/verify_census_data.py --backfill` |

No migration. Table unchanged. Census Median HHI is in `average_household_income`; the app shows it as **"Median Household Income (MHI)"**.
