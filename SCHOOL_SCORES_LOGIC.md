# How School Scores Get on the Map (Step-by-Step)

This document walks through the logic from **user enters an address** to **school names and ratings appear on the UI**.

---

## 1. User enters an address

- User types an address in the search box and submits (or selects a place).
- The **frontend** (`frontend/static/js/map.js`) runs the search flow: it geocodes the address with the Google Maps Geocoding API to get `lat` and `lng`, then calls `fetchAndDisplaySchoolScores(address, lat, lng)`.

---

## 2. Frontend calls the backend

- The browser sends a **GET** request to:
  - **URL:** `/api/schools/address`
  - **Query params:** `address`, `lat`, `lng` (lat/lng may be from the map if the user already had a location)
- If the request didn’t include `lat`/`lng`, the **backend** geocodes the address with Google first, then uses that `lat`/`lng` for all school logic.

---

## 3. Backend: how we get “the schools” for this address

We are **not** using attendance-zone boundaries (true zoning) here. We use **two sources**, in order:

### Step A – Apify (primary)

1. **Build a 2-mile box** around the address:
   - From `lat`/`lng`, we compute a bounding box (e.g. ± ~2 miles in lat/lng).
2. **Call Apify** (Zillow School Scraper) with that box:
   - The Apify actor scrapes Zillow/GreatSchools for schools in the box.
   - It returns a **list of schools** in that area (with names, levels, etc.).
3. **Pick one school per level** (elementary, middle, high):
   - From that list we **choose the single closest school of each level** to the address (by distance).
   - So we end up with at most **one elementary, one middle, one high** — these are “schools near this address by proximity,” not necessarily the official zoned schools.

**Important:** The Apify actor does **not** take an address; it only takes a bounding box. So we always use “schools in a 2-mile box” + “closest of each level” as a stand-in for “schools for this address.”

### Step B – Match to our ratings database

- We have a **Supabase table `school_data`** with school names and ratings (e.g. GreatSchools-style ratings).
- For each of the three names from Apify (elementary, middle, high), we:
  1. Look up a row in `school_data` where the **name matches** (exact, or `ILIKE` partial match) and the **rating is not null**.
  2. If we **find** such a row → we use that row’s **name**, **rating**, and **address** for the API response.
  3. If we **don’t** find such a row → we **do not** return that school at all (no name, no rating). So we **only show a school when we have a rating** for it.

So “zoned” in practice here means: **schools we decided to show for this address** (from Apify + DB match). We only show them when we have a rating.

### Step C – Distance-based fallback (when Apify gives us nothing)

- If Apify **fails** (error, timeout) or returns **no schools** (or we couldn’t pick one per level), then:
  - We **do not** use NCES attendance zones.
  - We fall back to **distance-based** lookup:
    - We query `school_data` for rows that have **non-null** elementary (or middle or high) rating and **lat/lng**.
    - We compute distance from the address `lat`/`lng` to each row.
    - We pick the **nearest** row that has an elementary rating → that’s our “elementary” school; same idea for middle and high.
  - So the user still sees up to three schools (elementary, middle, high), but they are simply the **closest rated schools in our DB** by straight-line distance, not from Apify.

---

## 4. Backend response

- The backend returns JSON with (for each level, when we have a match):
  - `elementary_school_name`, `elementary_school_rating`, `elementary_school_address`
  - `middle_school_name`, `middle_school_rating`, `middle_school_address`
  - `high_school_name`, `high_school_rating`, `high_school_address`
  - `blended_school_score` (average of the ratings we have).
- If we didn’t find a rated match for a level, those fields are `null` for that level.

---

## 5. Frontend: what gets printed on the UI

- The frontend receives that JSON and updates the **School Scores** section:
  - **If** the API sent a **non-null rating** for a level (e.g. `elementary_school_rating`):
    - It shows the **school name** (e.g. `elementary_school_name`) and the **rating** (and blended score when available).
  - **If** the API did **not** send a rating for that level (value is `null` or missing):
    - It shows **“N/A”** for the score and **“No data available”** for the name.

So the user only sees a **school name** when we have a **rating** for it; otherwise they see “No data available” and “N/A.”

---

## Summary flow (one sentence per step)

1. User enters address → frontend geocodes it and calls `/api/schools/address?address=...&lat=...&lng=...`.
2. Backend (optionally) geocodes address to get `lat`/`lng`.
3. **Primary path:** Apify returns schools in a 2-mile box; we pick the **closest** elementary, closest middle, closest high by distance.
4. We **match** those three names to `school_data` **only** where a rating exists; if no match, we don’t return that school.
5. **Fallback:** If Apify gives us nothing, we use the **nearest** rows in `school_data` (with ratings) by distance for each level.
6. Frontend shows **name + rating** only when the API sent a rating; otherwise “No data available” and “N/A.”

---

## How we’re deciding “the zoned schools”

- **We are not** using official attendance zones (e.g. NCES polygons) in this flow.
- We **are** using:
  1. **Apify:** “Schools in a 2-mile box around the address” → then **closest one per level** (elementary, middle, high).
  2. **Ratings filter:** Only schools that **exist in our `school_data` table with a non-null rating** are shown.
  3. **Fallback:** If Apify doesn’t give us anything, the **closest** rated schools in `school_data` by distance (one per level).

So “zoned” here really means **“schools we’ve chosen to show for this address”** (by proximity + rating availability), not strict zoning boundaries.
