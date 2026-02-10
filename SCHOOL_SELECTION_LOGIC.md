# School Selection Logic — What Actually Drives the UI

This doc explains **exactly** what produces the elementary / middle / high school names and ratings when you look up an address in the app.

---

## Current behavior: distance-only (no Apify)

When you use **Search Address** and click **Go**, the app calls `GET /api/schools/address?address=...&lat=...&lng=...`. The backend uses **only** this path:

| Source | When it’s used | What it means |
|--------|-----------------|----------------|
| **`apify`** | Apify returns schools in a 2-mile box **and** at least one of those school names matches a row in `school_data` with a rating. | Schools shown are: **Apify’s “closest” elementary/middle/high in that 2-mile box**, then matched to your DB for ratings. **Not** true attendance-zone zoning. |
| **`distance_fallback`** | Apify fails, returns nothing, or none of its school names match `school_data` (with a rating). | Schools shown are: **nearest** elementary, nearest middle, nearest high from `school_data` within about **5 miles** of the address (by distance), with ratings. |

The API response includes **`school_source`**; for this endpoint it is always **`"distance_fallback"`** (Apify is no longer called). See `scripts/reference_school_address_with_apify.md` for the previous Apify + fallback flow.

---

## Step-by-step (what the code does now)

1. **Try Apify**
   - Build a **2-mile box** around the address (lat/lng).
   - Call Apify Zillow School Scraper with that box → get **all** schools in the box.
   - For each level (elementary, middle, high), pick the **single closest** school to the address (by straight-line distance).
   - So the “zoned” schools in the UI are really **“closest in 2-mile box”**, not strict attendance boundaries.

2. **Match to your database**
   - For each of those three school **names**, look up a row in `school_data` that has a rating (elementary_school_rating, middle_school_rating, or high_school_rating).
   - Match is by name: exact first, then `ILIKE %name%`.
   - Only schools that **have a matching row with a rating** are shown. If Apify returns a school name that isn’t in `school_data` or has no rating, that level is left blank for the Apify path.

3. **Fallback if Apify doesn’t give you anything usable**
   - If **no** elementary, middle, or high from the Apify path end up with a DB match (or Apify failed/empty), the backend uses **distance_fallback**.
   - It queries `school_data` for the **nearest** row (by distance) that has:
     - `elementary_school_rating` (for elementary),
     - `middle_school_rating` (for middle),
     - `high_school_rating` (for high),
   - within about **5 miles** (lat/lng box).
   - Those nearest-by-distance schools (and their ratings) are what you see on the UI when `school_source === "distance_fallback"`.

---

## What is *not* used for the main address lookup

- **NCES attendance zones** (point-in-polygon) are **not** used for the schools shown in the main address lookup. They are used only for:
  - The “School Districts (zip)” layer on the map, and
  - The optional endpoint `GET /api/schools/address/all-zoned` (all NCES zones containing the point).
- So the “schools for this address” in the UI are **either**:
  - Apify’s closest-in-2-mile-box + DB match, **or**
  - Nearest in `school_data` within ~5 miles.

---

## How to see which source was used

1. **In the API response**  
   After a lookup, the JSON includes `school_source`:
   - `"apify"` → Apify 2-mile box + closest per level, matched to DB.
   - `"distance_fallback"` → Nearest schools in `school_data` within ~5 miles.

2. **Run the test script (with the app running)**  
   From the project root:
   ```bash
   python scripts/test_school_lookup_source.py "123 Main St, Charlotte, NC 28204"
   ```
   Or with explicit lat/lng:
   ```bash
   python scripts/test_school_lookup_source.py "123 Main St, Charlotte, NC 28204" 35.2271 -80.8431
   ```
   The script calls `GET /api/schools/address` and prints the returned schools and **`school_source`**.

3. **In the browser**  
   In DevTools → Network, select the request to `schools/address` and look at the JSON response for `school_source`.

---

## Summary

| Question | Answer |
|----------|--------|
| What produces the schools on screen? | **Either** Apify (closest in 2-mile box, then DB match) **or** nearest in `school_data` within ~5 miles. |
| Is it true “zoned” by attendance boundary? | No. The main address lookup uses **Apify closest + DB** or **distance fallback**, not NCES point-in-polygon. |
| How do I know which one ran? | Check the API response field **`school_source`**: `"apify"` or `"distance_fallback"`. |
| Where do the ratings come from? | Always from your **`school_data`** table (GreatSchools or whatever populates that). Apify only supplies **names**; we match those names to DB rows to get ratings. |

This is the final behavior for “GreatSchools selection and zoned schools logic” in the app unless you change the code to use NCES zoning for the main address result.
