# Address → Zoned Schools: Step-by-Step Walkthrough

This doc walks through **exactly what happens** when someone enters an address on the map: the layers, the process, how the three zoned schools (elementary, middle, high) are determined, and **why one or two of them sometimes stay blank**.

---

## 1. What the User Does

1. User types an address in the search box (e.g. "1111 Metropolitan Ave, Charlotte, NC 28204").
2. User submits (Enter or search button).
3. The map geocodes the address, centers the map, and then **requests school data** for that address from your backend.
4. The backend runs the logic below and returns **elementary_school_name**, **middle_school_name**, **high_school_name** and their **ratings** (or null).
5. The frontend displays:
   - **If a level has data:** score (e.g. 7.2) and school name.
   - **If a level is null/blank:** "N/A" for score and "No data available" for name.

So "blank" in the UI = that level came back as `null` from the API (no zoned school found, or no rating found for that school).

---

## 2. High-Level Flow (Layers)

```
User enters address
       ↓
[Layer 0] Geocode address → lat, lng
       ↓
[Layer 1] Try Apify (GreatSchools/Zillow) → get up to 3 school names (elem, middle, high)
       ↓
  Success? → use those names
  Fail?    → [Layer 2] Try NCES attendance zones (point-in-polygon) → get up to 3 names
       ↓
  Any names? → [Layer 3] Match names to school_data → get ratings
  No names?   → [Layer 4] Distance-based fallback → closest school of each type in DB
       ↓
Build response: elementary/middle/high name + rating (or null)
       ↓
Frontend shows score + name, or "N/A" / "No data available" for blank levels
```

So the **layers** are:

- **Layer 0:** Geocoding (address → lat/lng).
- **Layer 1:** Apify (primary source for zoned school **names**).
- **Layer 2:** NCES attendance zones (fallback for zoned school **names**).
- **Layer 3:** Match those names to `school_data` to get **ratings** (or leave null if no match).
- **Layer 4:** If no zoned names at all, distance-based lookup for closest schools in DB.

Each of the three levels (elementary, middle, high) is resolved **independently** in Layers 1–3 (or 4). So you can get, for example, elementary + high but blank middle.

---

## 3. Step-by-Step Process

### Step 0: Geocode the address

- **Where:** Backend `get_schools_by_address()` in `backend/routes.py`.
- **Input:** `address` from the request (and optionally `lat`/`lng` if the frontend already has them).
- **If lat/lng missing:** Backend calls Google Geocoding API with `address`, gets the first result’s `geometry.location` → `lat`, `lng`.
- **If geocoding fails:** API returns 400; user sees an error. No school lookup.
- **Output:** We now have `lat`, `lng` for all following steps.

---

### Step 1: Try Apify (GreatSchools/Zillow) — primary source for zoned school names

- **Where:** `backend/apify_client.py` → `get_schools_by_address(address, lat, lng, radius_miles=2.0)`.
- **What it does:**
  1. Builds a bounding box (~2 miles around the address).
  2. Calls Apify actor `axlymxp/zillow-school-scraper` with that box.
  3. Actor scrapes GreatSchools/Zillow for schools in the area.
  4. Apify returns a list of schools (each with level, name, coordinates, etc.).
  5. For **elementary**, **middle**, and **high** separately, the client:
     - Filters schools by that level (`schoolLevels` or similar).
     - Picks the **closest** school to (lat, lng) in that level.
  6. Returns a tuple: `(elementary_school_dict, middle_school_dict, high_school_dict)`.
- **Each of the three can be present or missing:**
  - If Apify returns no schools at all → `(None, None, None)`.
  - If Apify returns only elementary and high → middle is `None`.
  - If Apify times out or errors → exception; backend catches it and treats as “Apify failed.”
- **Backend then:** For each level, if the dict exists and has a name (`name` / `schoolName` / `title`), it sets e.g. `zoned_elementary = {'school_name': elem_name}`; otherwise that level stays `None`.
- **Result after Step 1:** Up to three zoned school **names** (elementary, middle, high). Any level can still be missing.

So **after Layer 1**, one or two levels can already be blank because:
- Apify didn’t return any schools, or
- Apify didn’t return any school for that **level** (e.g. no middle in the scraped set), or
- Apify returned a school but with no usable name, or
- Apify call failed (timeout, error).

---

### Step 2: If Apify didn’t give any zoned names → try NCES attendance zones

- **When:** Only if **no** level got a name from Apify (`not (zoned_elementary or zoned_middle or zoned_high)`).
- **Where:** `backend/routes.py` loads all NC/SC rows from `attendance_zones`, then `backend/zone_utils.py` → `find_zoned_schools(lat, lng, zones_list, level)` for each level.
- **What it does:**
  1. Load all attendance zones for **NC and SC** from DB.
  2. For **elementary:** Among zones with `school_level == 'elementary'`, find the zone whose GeoJSON polygon **contains** (lat, lng). If found, return that zone’s `school_name`.
  3. Same for **middle** and **high**.
- **Each level is independent:** The point might lie in an elementary zone but not in any middle zone (e.g. boundary quirk, or no middle zone in that area in NCES). So you can get elementary + high but blank middle from zones too.
- **Result after Step 2:** Again, up to three zoned school **names**; any level can still be `None`.

So **after Layer 2**, a level can still be blank because:
- We’re outside NC/SC (zones are only loaded for NC and SC).
- No attendance zone polygon for that **level** contains this (lat, lng).
- NCES data is school-year 2015–2016; boundaries may have changed; address might fall in a gap or in a different district in reality.

---

### Step 3: Match zoned school names to the database (get ratings)

- **When:** Whenever we have **at least one** zoned school name from Step 1 or Step 2.
- **Where:** Same `get_schools_by_address()` in `backend/routes.py`; for each level that has a name it runs several matching strategies against `school_data`.
- **What it does for each level (e.g. elementary):**
  1. **Exact match:** `school_data.elementary_school_name == elementary_name`.
  2. **Case-insensitive partial:** `elementary_school_name ILIKE '%{elementary_name}%'`.
  3. **Cleaned name:** Strip " School", " Elementary", " Elem", " PreK-8", etc.; match on cleaned.
  4. **Special cases:** e.g. if zone has "PreK-8", also try matching an "Elementary" version.
- **If a match is found:** We use that row’s `elementary_school_rating`, `elementary_school_name`, `elementary_school_address` for the response.
- **If no match is found:** We still **keep the zoned school name** from Apify/zones, but set **rating** (and sometimes address) to `None` for that level. So the API can return e.g. `elementary_school_name: "Some Charter Elementary"` and `elementary_school_rating: null` → frontend will show the name with "N/A" for the score.
- **If we never had a name for that level:** That level stays `null` in the response (name and rating both null) → frontend shows "N/A" and "No data available."

So **after Layer 3**, a level can show as “blank” (N/A / No data available) in two different ways:
- **No zoned name:** Step 1 and Step 2 never produced a school name for that level → name and rating both null.
- **Zoned name but no rating:** We have a name but no row in `school_data` matched it (or matched row has no rating) → we may still return the name with null rating; the UI typically shows "N/A" for the score and may show the name or “No data available” depending on how the frontend handles null rating.

(Checking frontend: it uses `schoolData.elementary_school_rating !== null && !== undefined` to decide whether to show the score or "N/A", and shows `schoolData.elementary_school_name || ''` or "No data available". So if name is present but rating is null, you’d typically see the name with "N/A" for score; if both are null, "No data available".)

---

### Step 4: If no zoned names at all → distance-based fallback

- **When:** Both Apify and attendance zones gave us **no** names for any level.
- **Where:** Same `get_schools_by_address()`; it runs three SQL queries (elementary, middle, high) with a ~5-mile bounding box and Haversine distance, and picks the **closest** school of each type in `school_data` that has a non-null rating.
- **Result:** We get at most one elementary, one middle, one high from the DB. If the DB has no school of that type within the box, that level stays null.
- So even here, one or two levels can be blank if there are no nearby schools of that type in `school_data`.

---

## 4. How the Response Is Built and What the Frontend Shows

- Backend always returns an object with:
  - `elementary_school_name`, `elementary_school_rating`, `elementary_school_address`
  - `middle_school_name`, `middle_school_rating`, `middle_school_address`
  - `high_school_name`, `high_school_rating`, `high_school_address`
  - `blended_school_score` (average of present ratings, or null)
- Any of these can be `null` if we never found a school for that level or never found a rating.
- Frontend (`map.js`):
  - If `elementary_school_rating` is not null/undefined → show score and `elementary_school_name` (or empty string).
  - Else → show "N/A" and "No data available" for that row.

So “blank” for a level = that level’s name and/or rating are null in the API response.

---

## 5. Why One or Two of the Three Levels Stay Blank — Summary

| Reason | Which layer | What happens |
|--------|-------------|--------------|
| Apify returned no schools | Layer 1 | All three null unless Step 2 (zones) fills some. |
| Apify returned schools only for some levels | Layer 1 | e.g. only elementary and high; middle stays null until/unless zones fill it. |
| Apify failed (timeout, error) | Layer 1 | All from Apify are null; we go to Step 2. |
| Address outside NC/SC | Layer 2 | Attendance zones never run (or we only have NC/SC zones), so zones don’t add anything. |
| Point not inside any zone for that level | Layer 2 | e.g. (lat,lng) inside an elementary zone but not inside any middle zone → middle stays null. |
| NCES zones outdated or incomplete | Layer 2 | Real-world boundary or level might not exist in 2015–2016 data. |
| Zoned name found but no match in school_data | Layer 3 | We may return name with null rating → "N/A" for score; or if we don’t return name when rating is null, that level looks “blank.” |
| No rating in school_data for matched school | Layer 3 | Same as above: name maybe present, rating null → "N/A" for score. |
| Distance fallback: no school of that type in 5 mi | Layer 4 | That level stays null. |

So blanks are expected when:
- The **primary source (Apify)** doesn’t return a school for that level, or
- The **fallback (attendance zones)** doesn’t cover that address/level, or
- We have a **zoned school name** but **no rating** in your DB, or
- We’re in **distance-only** mode and there’s **no school of that type** nearby in `school_data`.

---

## 6. Quick Reference: Code Locations

| Step | File | Function / logic |
|------|------|------------------|
| Geocode | `backend/routes.py` | `get_schools_by_address()` — Google Geocoding API when lat/lng missing |
| Apify | `backend/apify_client.py` | `get_schools_by_address()` → `get_schools_by_bounds()` then `_find_closest_school()` per level |
| Attendance zones | `backend/routes.py` | Query `AttendanceZone` for NC/SC; then `find_zoned_schools()` per level |
| Point-in-polygon | `backend/zone_utils.py` | `find_zoned_schools(lat, lng, zones_list, 'elementary'|'middle'|'high')` |
| Name → rating | `backend/routes.py` | Multiple `SchoolData` query strategies per level |
| Distance fallback | `backend/routes.py` | Three Haversine queries for closest elem/mid/high in `school_data` |
| Response | `backend/routes.py` | Build `result` with elementary_*, middle_*, high_*, blended_school_score |
| Display | `frontend/static/js/map.js` | `fetchAndDisplaySchoolScores()` — shows score/name or "N/A" / "No data available" |

---

## 7. End-to-End Example

**Address:** "1111 Metropolitan Ave, Charlotte, NC 28204"

1. **Geocode** → lat/lng for that address.
2. **Apify** runs (may take 30–60 s). Returns e.g. Sedgefield Elementary, Sedgefield Middle, Myers Park High.
3. Backend sets `zoned_elementary`, `zoned_middle`, `zoned_high` from those names.
4. **Match to DB:** Look up each name in `school_data`; get ratings and addresses.
5. **Response:** All three names + ratings (or null for any missing).
6. **Frontend:** Shows three rows with scores and names, or "N/A" / "No data available" for any missing level.

**If Apify failed:** Step 2 would use NCES zones; (lat, lng) might fall in one elementary zone, one middle zone, one high zone → same idea. If (lat, lng) falls in only two zones, the third level stays blank. If we’re outside NC/SC or in a gap in the zone data, all three can stay blank and we’d use distance-based fallback (Layer 4).

This is the full logic and why one or two of the three zoned schools (elementary, middle, high) can remain blank for a given address.
