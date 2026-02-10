# Zoning School Logic — FAQ

Answers to common questions about how we determine the three zoned schools (elementary, middle, high) for an address.

---

## 1. Step 1 (Apify): Do we sometimes get blanks because there are no schools within the 2-mile radius?

**Yes.** In Step 1 we call Apify with a **~2-mile bounding box** around the address. Apify returns **all schools in that area** (from GreatSchools/Zillow). We then pick the **closest** school of each level (elementary, middle, high) by distance.

So a level can be blank when:

- **No schools of that level** were returned by Apify in the 2-mile box (e.g. rural area, or the scraper didn’t find any middle schools).
- **Apify failed** (timeout, error) — then all three from Step 1 are blank and we use Step 2 (NCES) for any level.
- **Apify returned schools** but with no usable **name** for that level — we treat it as blank.

So “no schools within that two-mile radius” (or none found by the scraper for that level) is one reason Step 1 can leave one or two levels blank.

---

## 2. Step 2 (NCES): Is it only when ALL three are blank, or can it run when 2 out of 3 are blank?

**We changed this.** Previously, Step 2 (NCES attendance zones) ran **only when all three** were blank from Apify (`if not use_zones`).

**Now:** Step 2 runs for **any level that is still blank** after Step 1. So:

- If Apify returns only **elementary**, we still run Step 2 and fill **middle** and **high** from NCES (point-in-polygon) when the address is in NC/SC.
- If Apify returns **elementary** and **high** but not middle, we fill **middle** from NCES.
- If Apify returns nothing, we fill all three from NCES (same as before).

So Step 2 is no longer “only when all blank” — it **fills in whichever levels are still blank** (using NCES for NC/SC only).

---

## 3. Step 2 (NCES): We select the first match — can we get a list of ALL schools the address is zoned for?

**Yes.** For the **main flow** we still use **one zone per level**: `find_zoned_schools()` returns the **first** zone (in DB order) whose polygon contains the address for that level. So we show one elementary, one middle, one high.

If you want **all** NCES zones that contain the address (e.g. for a dropdown or export):

- **New helper:** `find_all_zoned_schools(lat, lng, zones)` in `backend/zone_utils.py` returns **every** zone whose polygon contains the point, **grouped by level**:  
  `{'elementary': [zone1, ...], 'middle': [...], 'high': [...]}`.  
  There can be 0, 1, or more zones per level (e.g. overlapping boundaries).

- **New API:**  
  **`GET /api/schools/address/all-zoned?address=...`** or **`?lat=...&lng=...`**  
  Returns all NCES zones (NC/SC) that contain that point, grouped by level, with `school_name`, `school_level`, `school_district`, `state` for each. You can use this for:
  - A **dropdown** in the app: “All zoned schools for this address.”
  - **Export**: include “All zoned schools (NCES)” in the report by calling this endpoint for the same address and appending the result.

Example:

```text
GET /api/schools/address/all-zoned?address=123 Main St, Charlotte, NC 28204
```

Response (conceptually):

```json
{
  "address": "123 Main St, Charlotte, NC 28204",
  "latitude": 35.22,
  "longitude": -80.84,
  "elementary": [{"school_name": "Sedgefield Elementary", "school_level": "elementary", "school_district": "...", "state": "NC"}],
  "middle": [{"school_name": "Sedgefield Middle", ...}],
  "high": [{"school_name": "Myers Park High", ...}]
}
```

So: main flow still uses “first match” per level; for a **full list** (dropdown/export), use the new helper or **`/api/schools/address/all-zoned`**.

---

## 4. Why do we use a 2-mile radius for Apify? Why can’t we just enter the address and get the 3 zoned schools?

**We’d prefer “address in → 3 zoned schools out.”** We can’t do that with the **current Apify actor** because it **does not accept an address**. It only accepts a **bounding box** (north/south/east/west). It returns **all schools in that area**, not “the 3 zoned schools for this address.” Zillow’s website shows assigned schools per address; the actor doesn’t support that — it only does “schools in this region.”

So we:

1. Geocode the address to (lat, lng).
2. Build a **~2-mile box** around it.
3. Call the actor with that box → get all schools in the area.
4. Pick the **closest** elementary, middle, and high by distance as a **proxy** for “zoned.”

That’s why we use a 2-mile radius: the actor **only** supports a box. “Closest” can be wrong when the true zoned school is farther away (e.g. charter nearby, or different attendance boundary).

**What would be better:** An actor or API that accepts **address** (or lat/lng) and returns the **3 zoned schools** for that address (like Zillow’s UI). Until we have that, we keep “2-mile box + closest” and treat it as a known limitation.

See **`APIFY_WHY_BOUNDS_AND_CLOSEST.md`** and **`APIFY_DATA_REFERENCE.md`** (§ 4a) for more detail.

---

## Summary

| Question | Answer |
|----------|--------|
| Step 1 blanks from no schools in 2 miles? | Yes — no (or no usable) schools of that level in the box can leave that level blank. |
| Step 2 only when all blank? | No — **now** Step 2 fills **any level still blank** after Apify (not only when all three blank). |
| First match vs all zoned schools? | Main flow uses **first match** per level. For **all** zoned schools use `find_all_zoned_schools` or **GET /api/schools/address/all-zoned**. |
| Why 2-mile radius / why not address → 3 schools? | Apify actor only accepts a **bounding box**, not an address; we use 2-mile box + closest as a proxy. See APIFY_WHY_BOUNDS_AND_CLOSEST.md. |
