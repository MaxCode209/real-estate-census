# Census Data Update — What We're Doing

This doc spells out exactly how we update the **census_data** table when we pull in 2024 data.

---

## 1. What We Update (Your Checklist)

We update the **census_data** table so that each row has:

| # | Field | Source | Notes |
|---|--------|--------|--------|
| 1 | **state** | Census geography (FIPS → 2-letter code) | e.g. "37" → "NC" |
| 2 | **county** | Census geography (FIPS → name when lookup exists) | From same geography as state |
| 3 | **population** | 2024 value from Census | B01001_001E — "new population" |
| 4 | **median_age** | 2024 value from Census | B01002_001E — "new median age" |
| 5 | **average_household_income** | 2024 value, computed | (B19025_001E / B11001_001E) — "new avg household income" |
| 6 | **total_households** | 2024 value from Census | B11001_001E — **new column** |
| 7 | **owner_occupied_units** | 2024 value from Census | B25003_002E |
| 8 | **renter_occupied_units** | 2024 value from Census | B25003_003E |
| 9 | **moved_from_different_state** | 2024 value from Census | B07001_017E — people who moved from another state in the past year |
| 10 | **moved_from_different_county** | 2024 value from Census | B07001_033E — people who moved from another county (same state) in the past year |
| 11 | **moved_from_abroad** | 2024 value from Census | B07001_049E — people who moved from abroad in the past year |
| 12 | **net_migration_yoy** | **Calculated by us** | See below |

---

## 2. How net_migration_yoy Is Calculated

**Formula:**

```text
net_migration_yoy = (population_2024 - population_2023) / population_2023 * 100
```

- **population_2024** = the 2024 population we just fetched for that zip.
- **population_2023** = the population already stored for that zip (from when the row had 2023 data).

So:

- We are **not** using the “moved from” variables to compute net_migration_yoy.
- We **are** using them only as stored fields (moved_from_different_state, moved_from_different_county, moved_from_abroad).
- Net migration is **only** the year‑over‑year population change as a percentage.

**Where it’s done:** In `scripts/fetch_census_data.py`, inside `_store_batch()`, when we have both:

- 2024 data for that zip (from the API), and  
- An existing row for that zip with `data_year == '2023'` and a non‑zero population.

If we don’t have 2023 data for that zip, we leave **net_migration_yoy** as `NULL`.

---

## 3. Flow in Plain English

1. We decide which zips to update (e.g. all zips from the DB via `--from-db`, or a list via `--zip-codes`).
2. For 2024, we call the Census API and get, for each zip:
   - state, county (from geography),
   - population, median_age, average_household_income (and the inputs for it),
   - total_households, owner_occupied_units, renter_occupied_units,
   - moved_from_different_state, moved_from_different_county, moved_from_abroad.
3. We write those 2024 values into the **census_data** row for that zip (overwriting the row with 2024 data).
4. **Before** overwriting, we look up the current row’s **population** and **data_year**:
   - If that row is 2023 data, we treat that population as **population_2023**.
   - We set  
     `net_migration_yoy = (population_2024 - population_2023) / population_2023 * 100`  
     and store it on the same row we’re updating.
5. So after the run, that row holds **2024** data plus the one calculated field **net_migration_yoy** from (2024 − 2023) / 2023.

---

## 4. Summary Table

| Your requirement | Our implementation |
|------------------|---------------------|
| Update **state** | From Census geography; FIPS → 2-letter state code |
| Update **county** | From Census geography; FIPS → name when we have a lookup |
| New **population** | 2024 B01001_001E → `population` |
| New **median_age** | 2024 B01002_001E → `median_age` |
| New **avg household income** | 2024 (B19025/B11001) → `average_household_income` |
| **total_households** column | 2024 B11001_001E → `total_households` |
| **owner_occupied_units** | 2024 B25003_002E → `owner_occupied_units` |
| **renter_occupied_units** | 2024 B25003_003E → `renter_occupied_units` |
| **moved_from_different_state** | 2024 B07001_017E → `moved_from_different_state` |
| **moved_from_different_county** | 2024 B07001_033E → `moved_from_different_county` |
| **moved_from_abroad** | 2024 B07001_049E → `moved_from_abroad` |
| **net_migration_yoy** | **(population_2024 − population_2023) / population_2023 × 100** (only when we have 2023 data for that zip) |

So yes: we are updating the initial census_data table with state, county, new population, new median age, new avg household income, total_households, owner_occupied_units, renter_occupied_units, moved_from_different_state, moved_from_different_county, moved_from_abroad, and we are setting **net_migration_yoy** using **2024 population − 2023 population** as you specified.
