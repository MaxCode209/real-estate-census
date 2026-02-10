# Reference: School Address Lookup (Previous Logic with Apify)

This file preserves the **previous** behavior of `GET /api/schools/address` for reference. The main app now uses **distance-only** (nearest schools in `school_data` within ~5 miles); Apify is no longer called for this endpoint.

## Previous flow (saved for reference)

1. **Try Apify**
   - Build a 2-mile box around the address (lat/lng).
   - Call `ApifySchoolClient().get_schools_by_address(address, lat, lng, radius_miles=2.0)`.
   - Get back (elementary, middle, high) = closest school of each level in that box.
   - For each name returned, look up in `school_data` by exact name then `ILIKE %name%` for a row with a rating.
   - If any level matched, set `school_source = "apify"` and use those schools + ratings.

2. **Fallback if Apify didn’t yield usable schools**
   - If no elementary, middle, or high from step 1 (Apify failed, empty, or no DB match):
   - Set `school_source = "distance_fallback"`.
   - Query `school_data` for nearest row (by distance) that has:
     - `elementary_school_rating` (for elementary),
     - `middle_school_rating` (for middle),
     - `high_school_rating` (for high),
   - within ~5 miles (lat/lng box). Use those schools and ratings.

3. **Response**
   - Return schools + ratings and `school_source`: `"apify"` or `"distance_fallback"`.

## Why it was simplified

- Apify was often not providing usable matches for the DB (e.g. name/format mismatches), so the UI frequently fell back to distance anyway.
- Removing Apify from the address lookup and from the export report simplifies the flow and avoids external calls and latency.
- **Apify is no longer used in `routes.py` at all.** The only remaining use for `ApifySchoolClient` is **bulk downloading/importing schools** in scripts such as:
  - `scripts/bulk_import_schools.py` – import schools by region (e.g. NC/SC) via `get_schools_by_bounds`
  - `scripts/import_missing_schools.py` – fetch missing schools
  - `scripts/test_apify_schools.py` – test Apify connection

## Where the old code lived

- **Route:** `backend/routes.py` — `get_schools_by_address()` (the version that called Apify first, then distance fallback).
- **Client:** `backend/apify_client.py` — `ApifySchoolClient.get_schools_by_address()` (unchanged; still used elsewhere if needed).

## Test script (still valid)

- `scripts/test_school_lookup_source.py` — Calls `/api/schools/address` and prints schools + `school_source`. After simplification, `school_source` will always be `"distance_fallback"` for this endpoint.
