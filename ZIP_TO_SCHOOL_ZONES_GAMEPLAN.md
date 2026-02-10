# Zip Code → School Zones / Districts — Gameplan

## What You Want

When you enter a **zip code** (e.g. 28204):

1. **Segregate that zip** — see how many **different school zones** (or school districts) are in that zip. Example: 5 districts.
2. **List schools per district** — for each of those districts, see the list of schools (elementary, middle, high) that serve that zip.
3. **Compare strength** — see which school district is "strongest" in that zip (e.g. by ratings).

---

## Revert Done

Zoning logic is **reverted** to the old behavior: Step 2 (NCES) runs **only when Apify returned no schools for any level** (all three blank). So the map UI should load faster again.

---

## Feasibility — Yes, With What We Have

| Piece | What we have | Use |
|-------|----------------|-----|
| **Zip boundary** | ZCTA polygon for the zip (e.g. `data/zip_boundaries/28204.geojson` or Census TIGERweb). | Define the geographic area of the zip. |
| **Attendance zones** | NCES polygons in `attendance_zones` (NC/SC): `school_name`, `school_level`, `school_district`, `zone_boundary` (GeoJSON). | Each zone is one school’s attendance area (elem/mid/high). |
| **School ratings** | `school_data` with school names and ratings (elementary/middle/high). | Match zone school names to get ratings; aggregate per district for "strength." |

So we can:

1. Load the **zip polygon** for 28204.
2. Find **all attendance zones** whose polygon **intersects** the zip polygon (not point-in-polygon — polygon vs polygon). That gives every zone that touches or lies inside the zip.
3. **Group those zones by `school_district`** (we have `school_district` on each zone). That gives e.g. 5 distinct districts that serve part of 28204.
4. For each district, **list schools**: one row per zone (elementary, middle, high) that intersects the zip. So each district gets a list of schools (with name + level).
5. **Strength:** For each school, try to match `school_name` to `school_data` (same fuzzy matching we use elsewhere) to get ratings. Then per district compute an aggregate (e.g. average of elem/mid/high ratings, or blended score) and **rank districts** by that.

**Limitations:**

- **NC/SC only** — attendance zones are only loaded for NC and SC. Zip 28204 (Charlotte, NC) is in scope. Zips outside NC/SC would need another data source for zones.
- **ZCTA = zip** — We use ZCTA (Census) boundary for the zip. It’s a close proxy for the zip; boundaries are not identical to USPS delivery zip.
- **Performance** — For one zip we load the zip polygon once, then test **every** NC (or NC+SC) zone polygon for intersection. With ~6k zones that’s thousands of polygon-intersection checks. Shapely is fast; expect on the order of a few seconds per zip. We can optimize later (e.g. spatial index, or filter by state using census_data for the zip’s state).

---

## Thought Process & Gameplan

### Step 1: Zip boundary

- **Input:** Zip code (e.g. 28204).
- **Action:** Load ZCTA polygon for that zip.
  - First try: `data/zip_boundaries/28204.geojson` (if we have it).
  - Fallback: same logic as existing zip-boundary API (TIGERweb, etc.) to get GeoJSON for that ZCTA.
- **Output:** One Shapely polygon (or multi-polygon) for the zip.

### Step 2: Which zones intersect the zip?

- **Input:** Zip polygon; list of all NC/SC attendance zones (with `zone_boundary`, `school_name`, `school_level`, `school_district`, `state`).
- **Action:** For each zone, parse `zone_boundary` to a Shapely polygon and check `zip_polygon.intersects(zone_polygon)`. If True, that zone “serves” part of the zip.
- **Output:** List of zones that intersect the zip (each with school_name, school_level, school_district).

### Step 3: Group by district

- **Input:** List of intersecting zones.
- **Action:** Group by `school_district` (treat null/empty as “Unknown” or separate bucket). So we get e.g. 5 groups: District A, B, C, D, E.
- **Output:** Structure like:  
  `districts = [ { "district_id": "A", "district_name": "..." or same, "zones": [zone1, zone2, ...] }, ... ]`

### Step 4: Schools per district

- **Input:** Grouped districts (each with list of zones).
- **Action:** For each district, from its zones build the list of **schools** (e.g. one entry per zone: school_name + school_level). So each district has a list of schools (elementary, middle, high — possibly more than one per level if multiple zones overlap the zip).
- **Output:** For each district: `schools: [ { "name": "...", "level": "elementary" }, ... ]`

### Step 5: Ratings and “strongest” district

- **Input:** Per-district list of schools (name + level).
- **Action:** For each school, match name to `school_data` (existing fuzzy match: exact, ilike, cleaned name) and read the rating for that level (elementary_school_rating, middle_school_rating, high_school_rating). Compute per district an aggregate score (e.g. average of all school ratings in that district, or blended elem/mid/high). Sort districts by that score (e.g. descending).
- **Output:** Same list of districts, each with `schools` (now with `rating` where available) and `avg_rating` or `blended_score`, and the list sorted by strength.

### Step 6: API and UI

- **API:** New endpoint, e.g. `GET /api/zips/<zip_code>/school-zones` or `GET /api/schools/by-zip?zip=28204`, that:
  - Runs steps 1–5.
  - Returns: `{ "zip_code": "28204", "district_count": 5, "districts": [ { "district_id": "...", "schools": [...], "avg_rating": 7.2 }, ... ] }` (sorted by strength).
- **UI:** In the map app, when user enters or selects a zip (e.g. 28204), call this endpoint and show:
  - Number of districts in that zip (e.g. “5 school districts”).
  - List of districts, each with list of schools (and optionally ratings).
  - Which district is “strongest” (e.g. top of the list or highlighted).

---

## Cost

**This feature costs $0 in new API or data fees.**

| What we use | Cost |
|-------------|------|
| Zip boundary | Already have (local file or Census TIGERweb — **FREE**) |
| NCES attendance zones | Already in your DB (one-time import — **FREE**) |
| school_data ratings | Already in your DB (no new Apify or external calls) |
| Polygon intersection / grouping | Local computation (Shapely, your server — **no per-request fee**) |

We do **not** call Apify, Census API, or any other paid service for “zip → districts.” Everything runs on data you already have and local geometry. So **no ongoing cost** for this gameplan.

---

## UI: Zip Highlighted + District Layers Inside

**Yes — we can keep the zip highlighted and layer the different school districts inside it.**

**Idea:**

1. **Zip stays as now** — When the user enters/selects a zip (e.g. 28204), the zip boundary is still drawn and highlighted the way it is today (e.g. outline or fill).
2. **District layer inside the zip** — We compute, for each district that touches the zip, the **piece of the zip that lies in that district**: i.e. the **intersection** of (zip polygon) with (all zone polygons in that district). That gives one polygon (or multi-polygon) per district that represents “this part of the zip is in District A,” “this part is in District B,” etc.
3. **Return geometries** — The API returns not only “list of districts and schools” but also **GeoJSON for each district’s slice** of the zip (the intersection polygon). So the frontend gets e.g. `districts[].geometry` = GeoJSON.
4. **Draw layers** — Frontend draws:
   - **Layer 1:** Zip boundary (current behavior — stays highlighted).
   - **Layer 2:** Each district’s geometry **inside** the zip, with a different fill (e.g. semi-transparent colors: District A = blue, B = green, C = orange, etc.). So the zip stays highlighted and inside it you see the different districts as colored/patterned areas.

**Implementation sketch:**

- **Backend:** When building the “districts in this zip” response:
  - For each district, take all zones in that district that intersect the zip.
  - For each zone, compute `zip_polygon.intersection(zone_polygon)` (Shapely). Merge those intersection polygons (union) per district so you have one geometry per district = “the part of the zip in this district.”
  - Add to each district object: `geometry: <GeoJSON>` (and optionally a `fill_color` or `color_index` for the frontend).
- **Frontend:** When displaying the selected zip:
  - Request the school-zones endpoint for that zip (e.g. `GET /api/zips/28204/school-zones`).
  - Draw the zip boundary (existing logic).
  - For each district in the response, if it has `geometry`, draw that geometry as a separate map layer (polygon fill) with the chosen color. Optionally a legend: “District A (blue), District B (green), …” and “Strongest: District A.”

So: **zip stays highlighted; districts are layered inside as separate polygons (different colors).** All from data we already have; no extra cost.

---

## How to Test (Implemented)

**Endpoint:** `GET /api/zips/<zip_code>/school-zones`

**Example (zip 28204):**  
http://127.0.0.1:5000/api/zips/28204/school-zones

**Requirements:**
- Zip boundary must exist: `data/zip_boundaries/{zip_code}.geojson` (e.g. run `python scripts/download_accurate_boundaries.py --zip-codes 28204` if missing).
- NCES attendance zones loaded for NC/SC (you already have these).

**Response shape:**
```json
{
  "zip_code": "28204",
  "district_count": 5,
  "districts": [
    {
      "district_id": "...",
      "district_name": "...",
      "schools": [{"name": "...", "level": "elementary", "rating": 7.2}, ...],
      "avg_rating": 7.1,
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "color": "#4A90D9"
    },
    ...
  ]
}
```
Districts are sorted by strength (avg_rating descending). First request may take 30–60 seconds (many polygon intersections).

---

## Implementation Order

1. **Revert** — Done: zoning logic back to “Step 2 only when all three blank.”
2. **Backend: zip → polygon** — Helper to load zip boundary as Shapely polygon (from file or existing boundary API).
3. **Backend: zone–zip intersection** — Function that takes zip polygon + list of zone dicts, returns list of zones that intersect the zip (using Shapely `intersects`).
4. **Backend: group by district** — From list of zones, group by `school_district` and build schools list per district.
5. **Backend: attach ratings** — Match school names to `school_data`, attach ratings, compute per-district score, sort.
6. **Backend: API** — `GET /api/zips/<zip>/school-zones` (or query param) that runs 2–5 and returns JSON.
7. **Frontend (optional)** — Zip input/selector that calls the API and displays district count, list of schools per district, and strongest district.

---

## Summary

- **Revert:** Done; map should load faster again.
- **Feasibility:** Yes. We have zip boundaries, NCES attendance zones with polygons and `school_district`, and `school_data` for ratings. We can do polygon–polygon intersection (zip vs zones), group by district, list schools per district, and rank by ratings.
- **Scope:** Works for zips in NC/SC (where we have attendance zones). 28204 is in NC, so in scope.
- **Next:** Implement steps 2–6 above (zip polygon helper, intersection, group by district, ratings, API, then UI if desired).
