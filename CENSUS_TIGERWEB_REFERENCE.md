# Census TIGERweb — Reference

This doc describes how **Census TIGERweb** (and related TIGER/Line data) is used in this project: source, year, purpose, update frequency, and where data is stored.

---

## 1. What It Is

- **TIGERweb** = US Census Bureau’s web mapping services for TIGER/Line geography.
- **TIGER/Line** = Official Census geographic boundary files (shapefiles, etc.).
- In this project we use them **only for ZCTA (Zip Code Tabulation Area) boundaries** — the polygon shapes for “zip codes” on the map.

---

## 2. Original Data Source

| Item | Details |
|------|--------|
| **Source** | US Census Bureau |
| **TIGERweb base** | https://tigerweb.geo.census.gov/ |
| **TIGER/Line page** | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html |
| **Cost** | FREE |
| **Format (API)** | ArcGIS REST → GeoJSON (via `f=geojson`) |
| **Format (bulk)** | Shapefile (e.g. `tl_20XX_us_zcta5XX.zip`) |

---

## 3. Year / Vintage

The project does **not** hard-code a single TIGER year everywhere; it uses a fallback order:

### TIGERweb REST API (used in app and download script)

1. **tigerWMS_Current** — “current” vintage (Census updates this; no year in the URL).
2. **tigerWMS_ACS2022** — 2022 vintage.
3. **tigerWMS_ACS2021** — 2021 vintage.

So the **effective year** is “current” when available, then 2022, then 2021.

### TIGER/Line shapefile (used in scripts only)

- `download_census_zcta.py` uses **TIGER2024**:  
  `https://www2.census.gov/geo/tiger/TIGER2024/ZCTA5/tl_2024_us_zcta510.zip`
- `auto_download_boundaries.py` tries **2023, 2022, 2021** in that order.

**Summary:**  
- **TIGERweb (API):** “Current” + 2022 + 2021 fallbacks.  
- **TIGER/Line (shapefile):** 2024 in one script; 2023/2022/2021 in another.  
- **No year is stored** in the boundary filenames or in the app; files are `{zip_code}.geojson`.

---

## 4. Update Frequency

- TIGER/Line shapefiles are **released once per year** (typically during the year, e.g. 2025 files released in 2025).
- Boundaries are intended to reflect geography **as of January 1 of that year** (with some updates through mid-year in recent vintages).
- **TIGERweb “Current”** is updated by Census to point at the latest release; we don’t control that schedule.

So: **yearly** updates from the Census Bureau; our app uses “current” when possible, then older vintages as fallback.

---

## 5. Purpose in This Project

| Purpose | Where |
|--------|--------|
| Draw zip code polygons on the map | Frontend requests boundary from API; API returns GeoJSON. |
| Populate local cache so we don’t re-fetch every time | Boundaries saved under `data/zip_boundaries/`. |
| Bulk download boundaries for all DB zips | `scripts/download_accurate_boundaries.py` uses TIGERweb. |
| Optional bulk ZCTA shapefile | `scripts/download_census_zcta.py` / `auto_download_boundaries.py` use TIGER/Line shapefiles. |

So TIGERweb/TIGER is **only for boundary geometry** (ZCTA polygons), not for demographic or census *data* (that comes from the Census API / ACS).

---

## 6. Where It’s Stored

| What | Where | Notes |
|------|--------|--------|
| **Local boundary cache** | `data/zip_boundaries/{zip_code}.geojson` | One GeoJSON file per zip. Used by API first (see below). |
| **Database** | Not stored | Boundaries are files + on-demand API, not in Postgres. |
| **Year/vintage** | Not stored | Filenames are `{zip_code}.geojson`; no year in path or in app. |

**API order of use (get boundary):**

1. **Local file:** `data/zip_boundaries/{zip_code}.geojson` (if present).
2. OpenDataSoft (external).
3. Boundaries.io (if key set).
4. GitHub (OpenDataDE).
5. **Census TIGERweb** (tigerWMS_Current, then ACS2022, ACS2021).
6. If all fail → 404; frontend can use an approximate boundary.

When the API successfully fetches from TIGERweb (or another source), it can **write** that result to `data/zip_boundaries/{zip_code}.geojson` so the next request is local.

---

## 7. Endpoints Used (TIGERweb)

| Endpoint | Layer | Use |
|----------|--------|-----|
| `.../TIGERweb/tigerWMS_Current/MapServer/2/query` | 2 = ZCTA | First choice in API and download script. |
| `.../TIGERweb/tigerWMS_ACS2022/MapServer/2/query` | 2 = ZCTA | Fallback. |
| `.../TIGERweb/tigerWMS_ACS2021/MapServer/2/query` | 2 = ZCTA | Fallback. |

Query parameters: `where` (e.g. `ZCTA5='28204'` or `ZCTA5CE10='28204'`), `outFields=*`, `f=geojson`, `outSR=4326`, `returnGeometry=true`.

---

## 8. Summary Table

| Question | Answer |
|----------|--------|
| **What is it?** | Census TIGERweb / TIGER/Line — official ZCTA boundary polygons. |
| **Original source?** | US Census Bureau (tigerweb.geo.census.gov, census.gov TIGER/Line). |
| **Year/vintage?** | TIGERweb: “Current” then 2022, 2021. Shapefile: 2024 (or 2023/2022/2021 in other scripts). Year not stored in filenames. |
| **Update frequency?** | Yearly (Census releases new TIGER/Line each year; “Current” follows that). |
| **Purpose here?** | ZCTA boundary geometry only (map polygons). |
| **Where stored?** | `data/zip_boundaries/{zip_code}.geojson`; no DB; no year in path. |

---

## 9. Related Files

- **API boundary logic:** `backend/routes.py` — `get_zip_boundary()` (local file first, then TIGERweb as source 4/5).
- **Bulk download from TIGERweb:** `scripts/download_accurate_boundaries.py` — writes to `data/zip_boundaries/`.
- **Bulk ZCTA shapefile:** `scripts/download_census_zcta.py` (TIGER2024), `scripts/auto_download_boundaries.py` (TIGER2023/2022/2021).
- **Docs:** `DATA_SOURCES_AND_LINKS.md`, `ACCURATE_BOUNDARIES_GUIDE.md`, `ZIP_BOUNDARY_COVERAGE.md`.
