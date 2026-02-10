# What Uses the Google Geocoding API (and How We Reduced It)

## What was driving ~33k+ requests

The **main source** of Geocoding API usage was the **map heatmap** in `frontend/static/js/map.js`:

- **`updateMap()`** runs when census data loads and **every time** you change a layer (Population / Income / Age) or toggle Zip Boundaries.
- It used to call **`geocodeZipCode(record.zip_code)`** for **every** census record.
- The app loads up to **5,000** records and passes them to the map.
- So: **one page load ≈ 5,000 Geocoding requests**, and **each layer/boundary toggle ≈ another 5,000**.
- A few loads + a few toggles could easily reach **15,000–30,000+** requests.

Other (much smaller) uses:

- **Search by zip** – 1 request per search (or fallback to backend `/api/geocode-zip/:zip`, which also uses the Geocoding API).
- **Search by address** – 1 request per search (frontend `geocoder.geocode`).
- **Export report** – if address is used without lat/lng, backend may geocode once per export.
- **School scores by address** – if lat/lng not provided, backend may geocode once per request.

So the map heatmap was responsible for the vast majority of your Geocoding bill.

---

## Changes made to cut usage

1. **Cap map to 300 zips**  
   The heatmap now uses at most the **first 300** census records per load. So instead of 5,000 geocode calls per load, you get at most **300** (and only for zips not yet in the cache).

2. **In-memory cache**  
   Geocoded zip → coordinates are stored in a **per-session cache** (`zipCoordCache`). Each zip is geocoded **at most once per session**; layer toggles and boundary toggles reuse the cache. So after the first `updateMap()`, further toggles add **0** new Geocoding requests for the same zips.

3. **UI note**  
   When there are more than 300 records, the UI shows something like: **“5000 (map: first 300)”** so it’s clear only the first 300 are drawn on the map.

**Rough effect:**  
- Before: e.g. 5,000 × (1 load + 3 toggles) = **20,000** requests.  
- After: at most **300** requests per session (first load), then **0** for toggles.  
So Geocoding usage from the map can drop by **~99%** for typical use.

---

## Where Geocoding is still used

| Trigger | Where | Approx. requests |
|--------|--------|-------------------|
| Map heatmap (first 300 zips, uncached) | `map.js` → `geocodeZipCode()` | ≤ 300 per session |
| Search by zip | `map.js` → `geocodeZipCodeFull()` | 1 per search |
| Search by address | `map.js` → `geocoder.geocode()` | 1 per search |
| Export report (no lat/lng) | `routes.py` → Geocoding API | 1 per export |
| School scores (no lat/lng) | `routes.py` → Geocoding API | 1 per request |
| Backend geocode-zip fallback | `routes.py` → `/geocode-zip/<zip>` | 1 per call |

---

## Optional: remove Geocoding from the map entirely

To **stop using the Geocoding API for the map at all**, you can use **zip centroids** (lat/lng per zip from a free source) instead of geocoding:

1. **Census Bureau** – e.g. “Gazetteer Files” (ZCTA lat/long):  
   https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html  
   Download the national ZCTA file and load it into a `zip_code_centroids` table (see `scripts/create_zip_centroids_table.py`).

2. **Backend** – Add an endpoint that returns coordinates for a list of zips from that table (e.g. `GET /api/zip-coordinates?zips=12345,67890`).

3. **Frontend** – In `updateMap()`, call that endpoint (in batches if needed) and use the returned coordinates for the heatmap instead of calling `geocodeZipCode()`. Then the map uses **0** Geocoding API requests.

If you want, we can wire the map to a zip-coordinates endpoint and only fall back to geocoding when centroids are missing.
