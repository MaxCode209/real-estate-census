# UI Features & Purpose

Overview of the current Real Estate Site Selection UI: what it does and what each part is for.

---

## Main page: Map + control panel

**URL:** `http://localhost:5000` (or `/`)

**Purpose:** View census and school data by zip code on a map, search by zip or address, and export a site report.

---

## 1. Data layers (left panel)

| Feature | What it does |
|--------|----------------|
| **Population** | Toggle heatmap by population. When checked (with Income/Age off), zip codes are colored by population; higher = warmer color. |
| **Median Household Income (MHI)** | Toggle heatmap by median household income. When checked, zip codes colored by income (priority over Age/Population if multiple on). |
| **Median Age** | Toggle heatmap by median age. When checked, zip codes colored by median age. |
| **Zip Code Boundaries** | Show/hide polygon outlines for each zip. When on, map draws zip boundaries (from local GeoJSON or API). |
| **School Districts (zip)** | Show/hide NCES school district polygons for the **currently searched zip**. Only loads after you search by zip; NC/SC only. Status text below explains “Loading…”, “Showing N district(s)”, or errors. |

**Behavior:** Only one heatmap metric is active at a time (priority: Income > Age > Population). Layer changes re-run the map (markers, heatmap, boundaries). Legend shows min/max for the active metric.

---

## 2. Search & zoom (left panel)

| Feature | What it does |
|--------|----------------|
| **Search Zip Code** | Enter a 5-digit zip, click **Go** (or Enter). Map zooms to that zip, draws its boundary if “Zip Code Boundaries” is on, loads census for that zip, and if “School Districts (zip)” is on, loads and draws NCES districts for that zip. |
| **Search Address** | Enter a full address, click **Go** (or Enter). Map geocodes the address, zooms to it, draws zip boundary if available, loads census for that zip, loads school districts for that zip if the checkbox is on, and **fetches school scores** (elementary/middle/high + blended) for that address and shows them in the **School Scores** section. |

**Note:** School scores (nearest schools in DB within ~5 miles) are only fetched when you use **Search Address**, not when you only search by zip.

---

## 3. Actions (left panel)

| Feature | What it does |
|--------|----------------|
| **Fetch Census Data** | POST to `/api/census-data/fetch` to pull census data from the Census API into the DB, then reloads the map with the updated census data. |
| **Download Report (Word/PDF)** | Generates a site report for the **current location**. Requires an address or zip from a prior search. Prompts Word (.docx) or PDF, then opens the export URL; report includes address, zip, census (e.g. population), and top schools (nearest in DB + additional up to 10). |
| **Refresh Map** | Reloads census data from the API (same as initial load) and redraws the map with current layer toggles. |

---

## 4. Info (left panel)

| Feature | What it does |
|--------|----------------|
| **Records loaded** | Shows how many census records are loaded. If more than 300, shows “300 (map shows first 300)” (heatmap is capped for performance). |

---

## 5. School scores (left panel)

| Feature | What it does |
|--------|----------------|
| **School Scores** | Hidden until you run **Search Address**. Then shows elementary, middle, and high school **names** and **ratings** (out of 10) plus a **blended score**, from the nearest schools in `school_data` within ~5 miles (no Apify). |

---

## 6. Map area

| Feature | What it does |
|--------|----------------|
| **Heatmap** | Zip-level intensity by the active layer (population, income, or age). Up to 300 zips geocoded and drawn; color gradient with legend. |
| **Markers** | One marker per zip (for the zips currently on the map). Clicking a marker opens an **info window** with that zip’s census: zip code, population, median age, MHI. |
| **Zip boundaries** | Polygons for each zip when “Zip Code Boundaries” is on. Highlight on hover/select. |
| **School district polygons** | When “School Districts (zip)” is on and a zip has been searched, NCES district polygons for that zip (NC/SC). Clicking a polygon shows district name, avg rating, and list of schools. |
| **Legend** | Min/max values and color for the active heatmap layer. |

---

## 7. Other pages

| Page | Purpose |
|------|--------|
| **/test** | Simple API connectivity check: GET `/api/census-data` and shows “API Working! Found N records” or an error. |

---

## Data flow (short)

- **Census:** Loaded from `/api/census-data` (DB). Optional bulk fetch via “Fetch Census Data” (Census API → DB).
- **Zip boundaries:** From `/api/zip-boundary/{zip}` (local GeoJSON or external APIs).
- **School districts (map):** From `/api/zips/{zip}/school-zones` (NCES zones intersecting that zip; NC/SC).
- **School scores (panel):** From `/api/schools/address?address=...&lat=...&lng=...` (nearest schools in `school_data` within ~5 miles).
- **Export report:** GET `/api/export/report?address=...&lat=...&lng=...&format=docx|pdf` (census + schools for that location).

---

## Files that define the UI

| File | Role |
|------|------|
| `frontend/templates/index.html` | Main layout: header, control panel (layers, search, actions, info, school scores), map div, legend. |
| `frontend/static/js/map.js` | All behavior: map init, census load, heatmap, markers, boundaries, school districts, search (zip + address), school scores fetch, export, event listeners. |
| `frontend/static/css/style.css` | Styling for layout, header, panel, buttons, legend, school scores, etc. |
| `frontend/templates/test.html` | Minimal test page for API connection. |

---

## Summary

The UI is built to:

1. **Visualize** census data (population, income, age) by zip on a heatmap with optional zip boundaries.
2. **Search** by zip (zoom + census + optional school districts for that zip) or by address (+ school scores for that address).
3. **Show** school scores (elementary/middle/high + blended) after an address search, from the nearest schools in the DB.
4. **Overlay** NCES school districts for a searched zip (NC/SC).
5. **Export** a Word or PDF site report for the current location (census + schools).
6. **Refresh** census from the API and refetch boundaries/layers as needed.

Use this list as the baseline when cleaning up or changing the UI.
