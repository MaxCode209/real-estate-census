# Real Estate Site Selection Tool – Complete Overview

This document explains what the app does, what data it contains after the census 2024 update, and how it is expected to work end-to-end.

---

## 1. What the App Is

The **Real Estate Site Selection Tool** is a web application that helps you evaluate locations (zip codes and addresses) for real estate decisions by:

1. **Visualizing census demographics** on an interactive map (population, income, age by zip code).
2. **Showing school ratings** (elementary, middle, high) for a given address, including zoned schools when available.
3. **Exporting** census data as CSV and **site reports** (Word/PDF) with demographics and top schools for an address.

It runs locally (Flask on port 5000), uses **Supabase (PostgreSQL)** for storage, and pulls census data from the **US Census Bureau API** and school data from **Apify (GreatSchools)** and optionally **attendance zone** boundaries (e.g. NC/SC).

---

## 2. Tech Stack and Architecture

- **Backend:** Python, Flask, SQLAlchemy.
- **Database:** PostgreSQL (Supabase). Connection and tables are created via `backend/database.py` and `backend/models.py`.
- **Frontend:** Single-page map UI – HTML/CSS/JS, Google Maps JavaScript API (map, heatmap, geocoding, Places).
- **Data sources:**
  - **Census:** US Census Bureau API (ACS 1-year), variables for population, median age, median household income, households, housing, mobility.
  - **Schools:** Apify actor (GreatSchools-style zoned schools by address); fallback: attendance zone polygons (NC/SC) with point-in-polygon.
  - **Boundaries:** Zip boundaries from local GeoJSON files (`data/zip_boundaries/*.geojson`), or OpenDataSoft / Boundaries.io APIs.

The app does **not** rename or add database columns for census (to avoid Supabase timeouts). The column **`average_household_income`** holds **Census Median Household Income (B19013)**; the UI labels it **“Median Household Income (MHI)”**.

---

## 3. Data in the App (Post Census 2024 Update)

### 3.1 Table: `census_data`

One row per **ZCTA (zip code)**. After you run **`python scripts/fetch_census_data.py --from-db --refresh`**, rows are filled/updated with **2024** Census values.

| Column | Meaning | Source |
|--------|--------|--------|
| `id` | Primary key | Auto |
| `zip_code` | Zip (ZCTA) code | Census geography |
| `state` | State (e.g. NC) | Kept in schema; not populated (avoids DDL) |
| `county` | County name | Kept in schema; not populated |
| `population` | Total population | Census B01001_001E |
| `median_age` | Median age | Census B01002_001E |
| `average_household_income` | **Median Household Income** | Census B19013_001E (stored here; shown as “MHI” in UI) |
| `total_households` | Total households | Census B11001_001E |
| `owner_occupied_units` | Owner-occupied housing units | Census B25003_002E |
| `renter_occupied_units` | Renter-occupied housing units | Census B25003_003E |
| `moved_from_different_state` | Moved from different state (past year) | Census B07001_017E |
| `moved_from_different_county` | Moved from different county, same state | Census B07001_033E |
| `moved_from_abroad` | Moved from abroad (past year) | Census B07001_049E |
| `net_migration_yoy` | (Pop 2024 − Pop 2023) / Pop 2023 × 100 | Computed when 2023 row exists |
| `data_year` | Year of census data (e.g. 2024) | Set on fetch |
| `created_at` / `updated_at` | Timestamps | Set on insert/update |

So after the refresh, **census_data** is your 2024 demographics store by zip: population, median age, **median household income** (in `average_household_income`), households, housing, mobility, and net migration when 2023 data exists.

### 3.2 Table: `school_data`

Stores **school ratings by address or zip**: elementary, middle, high school names and ratings (e.g. 1–10), plus a blended score. Filled when users search by address or when bulk imports run. Used to show “School Scores” in the UI and in reports.

### 3.3 Table: `attendance_zones`

Stores **school attendance zone boundaries** as GeoJSON (e.g. NC/SC). Used as a **fallback** when Apify does not return zoned schools: the app does point-in-polygon to find which zone contains the address and then looks up school names/ratings.

---

## 4. How the App Is Expected to Work

### 4.1 Starting the App

- Run: `python app.py`. Flask starts on `http://localhost:5000`. The index route serves the map page; API is under `/api/`.
- On first run, `init_db()` creates tables if they don’t exist.

### 4.2 Map and Census Layers

- **On load:** The frontend calls **GET /api/census-data** (with optional filters: zip, min/max income, min/max population, limit). The backend reads from `census_data` and returns JSON. The map then:
  - Geocodes each zip (or uses cached centroids) to get lat/lng.
  - Builds a **heatmap** and **markers** from that data.
  - Lets you choose which **layer** is shown: **Population**, **Median Household Income (MHI)**, or **Median Age** (and optionally **Zip Code Boundaries** from `/api/zip-boundary/<zip_code>`).
- **Clicking a marker** opens an info window with that zip’s census row: Zip, Population, Median Age, **Median Household Income (MHI)** (value comes from `average_household_income`).
- **“Refresh Map”** reloads census data from the API and redraws the map with the current layer and filters.

So the map is a **census demographics viewer by zip**: 2024 data from `census_data`, with income displayed as “Median Household Income (MHI)” even though the DB column is `average_household_income`.

### 4.3 Search and School Scores

- **Search by zip:** User enters a zip and clicks “Go”. The app zooms to that zip and can load census for it; boundaries come from `/api/zip-boundary/<zip_code>` if the layer is on.
- **Search by address:** User enters a full address and clicks “Go”. The app:
  - Geocodes the address (Google Geocoding).
  - Zooms the map to that location and optionally fetches **schools for that address** via **GET /api/schools/address?address=...&lat=...&lng=...**.
- **Schools by address** (backend):
  1. Tries **Apify** first (GreatSchools-style zoned schools for the address; can take 30–60 seconds).
  2. If Apify fails or returns nothing, falls back to **attendance zones** (NC/SC): point-in-polygon to find zoned schools, then looks up ratings in DB.
  3. Returns elementary, middle, and high school names and ratings; frontend shows them in the “School Scores” panel (and blended score).

So **school scores** are “zoned” schools when Apify or attendance zones succeed; otherwise the app may show nearby or no schools depending on implementation.

### 4.4 Export and Reports

- **CSV export:** **GET /api/export/csv** with the same filters as census-data (zip, income, population, etc.) returns a CSV of `census_data` rows (all columns). Used for “export current census view” type workflows.
- **Site report (Word/PDF):** **GET /api/export/report?address=...&format=docx|pdf**:
  - Geocodes the address, gets zip from result if not provided.
  - Loads **census_data** for that zip (one row) and puts it in the report as “Demographics” (Address, Zip, Population, **Median Household Income (MHI)**, Median Age).
  - Gets zoned schools (same logic as schools-by-address: Apify first, then zones), then top N schools with ratings.
  - Builds a Word or PDF with demographics + school table; zoned schools can be highlighted. All income in the report is **Median HHI** from `average_household_income`.

So after the census update, **all census numbers in the app and in exports/reports are 2024**, and income is consistently **Median Household Income (MHI)** from the Census (stored in `average_household_income`).

### 4.5 Fetching and Refreshing Census Data

- **One-off fetch (API):** **POST /api/census-data/fetch** with optional `zip_codes` calls the Census API and upserts into `census_data` (same fields as above, including B19013 → `average_household_income`).
- **Bulk refresh (script):**  
  **`python scripts/fetch_census_data.py --from-db --refresh`**  
  - Reads all zip codes from `census_data`, then in batches (e.g. 50 zips per batch) calls the Census API and **overwrites** those rows with 2024 data (population, median_age, average_household_income, total_households, owner/renter, moved_*, data_year, updated_at; net_migration_yoy if 2023 data exists).
  - No DDL is run; the table stays as-is (`average_household_income`, state, county columns unchanged). Progress is printed per batch (e.g. “Batch 7/676: 350/33774 zips (1%) — added 0, updated 50”).

So the **only** place census 2024 and Median HHI are “inserted” or updated is: **this script** (and the one-zip path when a zip is missing and fetched on demand). The app only reads from `census_data`; it does not create a separate “median_household_income” column.

---

## 5. End-to-End Expected Behavior (Summary)

1. **Database:** Supabase holds `census_data` (2024 demographics by zip, with **Median HHI in `average_household_income`**), `school_data` (address/zip school ratings), and `attendance_zones` (NC/SC boundaries). No schema change for census.
2. **Map:** Shows census 2024 by zip: heatmap + markers for Population, **Median Household Income (MHI)**, or Median Age; info window and legend use the same 2024 fields and label income as “MHI”.
3. **School scores:** For an address, the app shows zoned (or closest) elementary/middle/high and ratings, via Apify first and attendance zones as fallback.
4. **CSV export:** Exports filtered `census_data` (including `average_household_income` as the income field).
5. **Report export:** Word/PDF with demographics (Population, **Median HHI**, Median Age, etc.) and school table for the given address; income is from `average_household_income` and labeled “Median Household Income (MHI)”.

So in totality: the app is a **real estate site selection** tool that visualizes **2024 census data** (with Median HHI stored in `average_household_income` and displayed as “MHI”), shows **school ratings** for addresses, and exports **census + schools** to CSV and to Word/PDF reports. All census data post-refresh is 2024 and consistent with the Census Bureau’s median household income (B19013) and the other variables listed above.
