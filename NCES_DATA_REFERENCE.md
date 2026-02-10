# NCES Data — Reference

This doc describes how **NCES (National Center for Education Statistics)** school attendance boundary data is used in this project: source, year, purpose, update frequency, where it’s stored, and what variables we use.

---

## 1. What It Is

- **NCES** = National Center for Education Statistics (US Department of Education).
- **SABS** = School Attendance Boundary Survey — NCES’s collection of school attendance zone boundaries (polygons).
- In this project we use SABS **only for attendance zone polygons** so we can find which schools are zoned for a given address (point-in-polygon). We do **not** use NCES for school ratings or demographics; those come from Apify/GreatSchools and Census.

---

## 2. Original Data Source

| Item | Details |
|------|--------|
| **Source** | NCES (National Center for Education Statistics) |
| **Program** | EDGE (Education Demographic and Geographic Estimates) |
| **Product** | School Attendance Boundary Survey (SABS) |
| **Main URL** | https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries |
| **SABS home** | https://nces.ed.gov/programs/edge/sabs |
| **Data download** | https://nces.ed.gov/programs/edge/data/SABS_2015_2016.zip |
| **Cost** | FREE |
| **Format** | Shapefile (e.g. `.shp` / `.dbf` / `.shx`); we convert to GeoJSON for storage and point-in-polygon. |

---

## 3. Year / Vintage

| Item | Value |
|------|--------|
| **Data year in project** | **2015-2016** (SABS_1516) |
| **Stored in database** | `data_year = '2015'` (4-character field; script uses `'2015'` when importing from shapefile, `'2015-2016'` in GeoJSON import path). |
| **Shapefile naming** | SABS_1516 or similar (e.g. `sabs_1516_school.shp`). |

There is **no newer SABS release** in this project. NCES’s SABS was an experimental survey; the 2015-2016 collection was described as the final cycle. We do not currently use 2013-2014 or any other SABS vintage.

---

## 4. Update Frequency

- **SABS is not updated annually.** It was an experimental survey with two main cycles: 2013-2014 and 2015-2016. The 2015-2016 cycle was described as the final cycle of the experimental boundary collection.
- So in practice: **no ongoing update schedule** from NCES for SABS. Our project uses a **one-time import** of 2015-2016 data. To “update” you would need a different data source or a future NCES product if one is released.

---

## 5. Purpose in This Project

| Purpose | Where |
|--------|--------|
| **Find zoned schools for an address** | Given lat/lng, we do point-in-polygon against all attendance zone polygons (NC/SC). Whichever zones contain the point are that address’s zoned schools (elementary, middle, high). |
| **Fallback when Apify fails** | School lookup order: (1) Apify/GreatSchools, (2) NCES attendance zones. So NCES is used when the Apify scrape doesn’t return zoned schools. |
| **Display / export** | Zone boundaries and school names/levels are shown in the app and can be exported (e.g. `scripts/export_attendance_zones.py`). |

We do **not** use NCES for:
- School ratings (Apify/GreatSchools).
- Demographics (Census API).
- Boundaries for zip codes (Census TIGERweb).

---

## 6. Where It’s Stored

| What | Where | Notes |
|------|--------|--------|
| **Database table** | `attendance_zones` (Supabase/Postgres) | One row per zone: school name, level, state, district, GeoJSON polygon, `data_year`, `source`. |
| **Raw shapefiles** | `data/nces_zones/` (e.g. `data/nces_zones/SABS_1516/SABS_1516.shp`) | Optional; only if you download and place SABS shapefiles there. |
| **Processed GeoJSON** | `data/nces_zones/zones_nc_sc.geojson` | Optional; used only as fallback if shapefile import fails. |
| **Year/vintage** | `attendance_zones.data_year` | Stored as `'2015'` (or `'2015-2016'` in GeoJSON import path). |
| **Source label** | `attendance_zones.source` | Stored as `'NCES'`. |

The **authoritative** copy for the app is the **`attendance_zones`** table. The shapefiles/GeoJSON under `data/nces_zones/` are for import only.

---

## 7. Variables / Fields We Use

### From SABS shapefile (mapped into `attendance_zones`)

| SABS field | Description | Stored as |
|------------|-------------|-----------|
| `schnam` or `SCHNAM` | School name | `attendance_zones.school_name` |
| `level` or `LEVEL` | School level code: 1=Elementary, 2=Middle, 3=High, 4=Other | `attendance_zones.school_level` (mapped to `'elementary'`, `'middle'`, `'high'`, `'other'`) |
| `stAbbrev` or `STABBREV` | State abbreviation (e.g. NC, SC) | `attendance_zones.state` |
| `leaid` | LEA (district) ID | `attendance_zones.school_district` |
| Geometry | Polygon/multipolygon | `attendance_zones.zone_boundary` (GeoJSON text) |

### Database model (`AttendanceZone`)

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `school_id` | Integer (FK to school_data) | Optional link to school_data |
| `school_name` | String(255) | From SABS |
| `school_level` | String(50) | elementary / middle / high / other |
| `school_district` | String(255) | From leaid |
| `state` | String(2) | NC, SC (we filter to these) |
| `zone_boundary` | Text | GeoJSON polygon |
| `data_year` | String(4) | `'2015'` |
| `source` | String(100) | `'NCES'` |
| `created_at` / `updated_at` | DateTime | Metadata |

### Geographic coverage in this project

- **Import filter:** Only **NC (North Carolina)** and **SC (South Carolina)**.
- Filter uses SABS state field: `stAbbrev`/`STABBREV` in `['NC','SC']` or `STATEFP` in `['37','45']`.
- So we only store and query attendance zones for NC and SC.

---

## 8. How It’s Used in Code

1. **Import:** `scripts/import_nces_zones.py`
   - Looks for shapefiles under `data/nces_zones/` (any `*.shp`).
   - Reads with geopandas; filters to NC/SC; maps SABS fields to `AttendanceZone`; writes GeoJSON to `zone_boundary`; sets `data_year='2015'`, `source='NCES'`.
   - Fallback: import from `data/nces_zones/zones_nc_sc.geojson` if shapefile import fails.

2. **Lookup (zoned schools for an address):** `backend/routes.py` (and related logic)
   - Step 1: Try Apify/GreatSchools for zoned schools.
   - Step 2: If that fails, query `attendance_zones` for `state` in (NC, SC), then use `backend/zone_utils.py` to test if (lat, lng) is inside each zone’s `zone_boundary` (point-in-polygon). Return matching zones as zoned schools.

3. **Export:** `scripts/export_attendance_zones.py` — exports `attendance_zones` to CSV/JSON.

---

## 9. Summary Table

| Question | Answer |
|----------|--------|
| **What is it?** | NCES SABS — School Attendance Boundary Survey (attendance zone polygons). |
| **Original source?** | NCES EDGE; SABS shapefile (e.g. SABS_2015_2016). |
| **Year/vintage?** | 2015-2016 (stored as `data_year='2015'`). |
| **Update frequency?** | None — SABS was experimental/final; no ongoing NCES updates. |
| **Purpose here?** | Find zoned schools for an address (point-in-polygon); fallback after Apify. |
| **Where stored?** | `attendance_zones` table; optional raw files in `data/nces_zones/`. |
| **Variables used?** | schnam, level, stAbbrev, leaid, geometry → school_name, school_level, state, school_district, zone_boundary. |
| **Coverage?** | NC and SC only. |

---

## 10. Related Files

- **Model:** `backend/models.py` — `AttendanceZone` class.
- **Import:** `scripts/import_nces_zones.py` — download instructions, shapefile → DB, GeoJSON fallback.
- **Point-in-polygon:** `backend/zone_utils.py` — `point_in_polygon(lat, lng, geojson_boundary)`.
- **Lookup flow:** `backend/routes.py` — Apify first, then attendance zones for NC/SC.
- **Export:** `scripts/export_attendance_zones.py`.
- **Docs:** `DATA_SOURCES_AND_LINKS.md`, `ZONED_SCHOOLS_LOGIC.md`, `ADDRESS_SCHOOL_ISSUE.md`, `QUICK_START_LINKS.md`.
