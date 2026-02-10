# Apify Data — Reference

This doc describes how **Apify** (and the Zillow School Scraper actor) is used in this project: what it is, original data source, year/vintage, update frequency, where data is stored, what variables we use, and how it fits into the address → zoned schools flow.

---

## 1. What It Is

- **Apify** = Cloud platform for running “actors” (scrapers, automation). You call an API; the actor runs (e.g. scrapes a website) and returns results.
- **Actor we use:** **Zillow School Scraper** — `axlymxp/zillow-school-scraper` (or `axlymxp~zillow-school-scraper`).
- **Underlying data:** The actor scrapes **GreatSchools.org** and **Zillow** for school information (names, levels, ratings, locations). We do **not** call GreatSchools or Zillow directly; we only call Apify, which runs the scraper.
- **In this project:** Apify is the **primary source** for **zoned school names** when a user enters an address. The actor we use **only accepts a bounding box** (not an address), so we send a ~2-mile box, get all schools in that area, then pick the **closest** elementary, middle, and high by distance as a proxy for “zoned.” That’s a limitation of the actor—see **§ Why we use 2-mile radius + “closest”** below.

---

## 2. Original Data Source (What Apify Scrapes)

| Item | Details |
|------|--------|
| **Primary sites scraped** | GreatSchools.org, Zillow (school pages) |
| **Data we care about** | School name, school level (elementary/middle/high), rating (1–10), latitude/longitude |
| **Who provides it** | Apify actor runs in the cloud and returns JSON; the **source of truth** for the content is whatever GreatSchools/Zillow show at scrape time. |
| **We do not** | Call GreatSchools API or Zillow API directly; we have no fixed “dataset” from them—only what the scraper returns per run. |

So “Apify data” here = **live scraped results** from GreatSchools/Zillow, returned by the Apify actor. There is no separate “Apify dataset” with its own release year; the “vintage” is **the time of each actor run**.

---

## 3. Year / Vintage / Update Frequency

| Question | Answer |
|----------|--------|
| **Year released?** | N/A — data is **live**: whatever GreatSchools/Zillow show when the actor runs. |
| **Stored vintage?** | We don’t store a “data year” for Apify. For **address lookups** we don’t persist Apify results at all; we use them in-memory. For **bulk import** we write to `school_data` with no Apify-specific year field. |
| **Update frequency?** | **On each request** (for address lookup): each address triggers a new actor run (unless we add caching). So data is as fresh as the last scrape for that bounding box. Typical run: 30–60 seconds. |

So: no fixed “year”; “update” = every time we call the actor for that area.

---

## 4. Purpose in This Project

| Use case | What we do |
|----------|------------|
| **Address → zoned schools (primary)** | User enters address → we geocode to (lat, lng) → we call Apify with a ~2-mile bounding box (actor has no “address” input) → actor returns **all schools in that area** → we pick **closest** elementary, middle, high by distance as a proxy for zoned → we use those **names** only → we match names to `school_data` for ratings. **Note:** Zillow’s UI shows true zoned schools per address; the actor does not—see § Why we use 2-mile radius + “closest.” |
| **Bulk import / backfill** | Script `scripts/import_missing_schools.py` can call Apify by bounds, get many schools, and **write** them into `school_data` (name, rating, level, lat/lng). That’s the only place we “store” Apify data. |

We do **not** use Apify for:
- Census or demographic data (Census API).
- Zip boundaries (Census TIGERweb).
- Attendance zone polygons (NCES).

---

## 4a. Why We Use a 2-Mile Radius and "Closest" (Not True Zoned Schools)

**Your point is correct:** On Zillow (and GreatSchools), when you enter an address you see the **assigned/zoned** schools for that address—elementary, middle, high—and those are **not** always the geographically closest schools. We would prefer to "enter the address and get the 3 zoned schools" and match those names.

**Why we don't do that today:** The Apify actor we use (**axlymxp/zillow-school-scraper**) does **not** accept an address as input. Its input is **only** a geographic bounding box (east/west/north/south longitude/latitude). It returns **all schools in that area** from Zillow's API, not "the 3 zoned schools for this address." So we have no way, with this actor, to ask "what are the zoned schools for 123 Main St?" and get back exactly what Zillow shows.

**What we do instead:** We build a ~2-mile box around the address (geocoded lat/lng), call the actor with that box, get back a list of schools in the area, and then pick the **closest** school of each level (elementary, middle, high) by distance to the address. So "closest" is a **proxy** for "zoned"—and it can be wrong when the zoned school is farther away than another school in the box.

**Why 2 miles?** It's a heuristic: big enough to usually include the zoned schools, small enough to limit result size and cost. It doesn't fix the "zoned ≠ closest" issue.

**What would be better:** An actor (or API) that accepts **address** (or lat/lng) and returns the **3 zoned schools** for that address—like Zillow's property/school UI. Options: (1) Different Apify actor that supports "address in → zoned schools out"; (2) Request the axlymxp actor to add an address input; (3) Custom scraper that loads the Zillow/GreatSchools page for an address and extracts the 3 assigned schools. Until then, we stay with "2-mile box + closest." See **APIFY_WHY_BOUNDS_AND_CLOSEST.md** for a short summary.

---

## 5. Where It’s Stored

| Scenario | Where data lives | Notes |
|----------|------------------|--------|
| **Address lookup (map)** | **Not stored.** We call Apify → get list of schools → in-memory we pick closest elem/mid/high → extract names → match to `school_data` → return names + ratings to frontend. Apify response is discarded after the request. |
| **Bulk import** | **`school_data` table** (Supabase/Postgres). Script `import_missing_schools.py` uses Apify results to create/update rows (address, lat/lng, elementary_*, middle_*, high_* name/rating). No “Apify” table; we don’t store raw Apify JSON. |
| **Config** | **`APIFY_API_TOKEN`** in `.env`; **`APIFY_ZILLOW_SCHOOL_ACTOR_ID`** in `config/config.py` (optional; code uses hardcoded actor ID). |

So for the main flow (address on map), Apify data is **ephemeral**—used only to get school names for that one request.

---

## 6. How We Call Apify (Inputs)

- **API base:** `https://api.apify.com/v2`
- **Start run:** `POST https://api.apify.com/v2/acts/{actor_id}/runs` with JSON body.
- **Actor ID:** `axlymxp~zillow-school-scraper` or `axlymxp/zillow-school-scraper`.

**Input schema we send (from `backend/apify_client.py`):**

| Input key | Type | Description | Our typical value |
|-----------|------|-------------|-------------------|
| `eastLongitude` | string | East boundary longitude | From bounding box |
| `westLongitude` | string | West boundary longitude | From bounding box |
| `northLatitude` | string | North boundary latitude | From bounding box |
| `southLatitude` | string | South boundary latitude | From bounding box |
| `minRating` | int | Minimum school rating (1–10) | 1 |
| `includeElementary` | bool | Include elementary schools | true |
| `includeMiddle` | bool | Include middle schools | true |
| `includeHigh` | bool | Include high schools | true |
| `includePublic` | bool | Include public schools | true |
| `includePrivate` | bool | Include private schools | false |
| `includeCharter` | bool | Include charter schools | true |
| `includeUnrated` | bool | Include unrated schools | false |

**How the box is built for address lookup:** From (lat, lng) and `radius_miles=2.0` we compute north/south/east/west (lat/lng offset by ~2/69 degrees for latitude and a similar approximation for longitude). So we request schools within about **2 miles** of the address.

---

## 7. Variables / Fields We Use From Apify Response

The actor returns a **list of school objects**. We don’t control the exact schema; we tolerate multiple possible field names.

**Fields we read (in `backend/apify_client.py` and `scripts/import_missing_schools.py`):**

| Our use | Possible Apify field names | Description |
|---------|----------------------------|-------------|
| **School name** | `name`, `schoolName`, `title` | Display name; we use this to match to `school_data` and show in the UI. |
| **School level** | `schoolLevels` (array), or `level`, `schoolLevel`, `type`, `schoolType`, `gradeLevel` | We filter by `elementary`, `middle`, `high` to pick one school per level. |
| **Coordinates** | `latitude`/`longitude`, or `lat`/`lng`, or `y`/`x`, or `coordY`/`coordX` | We use these to find the **closest** school of each level to the address (lat, lng). |
| **Rating** | `rating`, `schoolRating` | Used only in **bulk import** when writing to `school_data`; not used in the address-lookup path (we get ratings from our DB after matching by name). |

So for **address lookup** we only need from Apify: **name**, **level**, and **coordinates**. Ratings in the API response could be used by the import script but are not used when resolving a single address.

---

## 8. Flow: Address Lookup (Layers)

1. User enters address → backend geocodes to (lat, lng).
2. Backend builds a ~2-mile bounding box around (lat, lng).
3. Backend calls `ApifySchoolClient.get_schools_by_address(address, lat, lng, radius_miles=2.0)`:
   - Which calls `get_schools_by_bounds(...)` → starts actor run with that box.
   - Waits for run to finish (polling up to 300 s, every 5 s).
   - Fetches dataset items (list of schools).
   - For each level (elementary, middle, high): `_find_closest_school(schools, level, lat, lng)` filters by level and picks the school with smallest distance to (lat, lng).
4. Returns `(elementary_dict, middle_dict, high_dict)` — each can be `None` if no school of that level in the results or all missing coordinates.
5. Backend extracts **name** from each dict (`name` / `schoolName` / `title`), then matches those names to `school_data` to get **ratings** (and addresses) and builds the JSON response for the frontend.

So Apify is **Layer 1** in the address → zoned schools walkthrough; NCES attendance zones are Layer 2 (fallback when Apify fails or returns no names).

---

## 9. Cost / Requirements

| Item | Details |
|------|--------|
| **Cost** | Apify is **pay-per-use** (credits per run/resource). Cost depends on actor pricing and run duration. Docs mention ~$10–50 for typical usage; bulk import can be more. |
| **API token** | **Required.** Set `APIFY_API_TOKEN` in `.env`. Without it, `ApifySchoolClient` raises; address lookup would fail and we’d fall back to NCES zones. |
| **Rate limits / timeouts** | We wait up to 300 seconds for the actor run. If it times out or fails, we get no schools from Apify and fall back to attendance zones. |

---

## 10. Summary Table

| Question | Answer |
|----------|--------|
| **What is it?** | Apify platform + Zillow School Scraper actor; data = live scrape of GreatSchools/Zillow. |
| **Original data source?** | GreatSchools.org, Zillow (scraped by the actor). |
| **Year / vintage?** | No fixed year; data is **live** at each run. |
| **Update frequency?** | Every time we call the actor (e.g. each address lookup, or each bulk import run). |
| **Purpose here?** | Primary source for **zoned school names** for an address; optional bulk import into `school_data`. |
| **Where stored?** | **Address lookup:** not stored (in-memory only). **Bulk import:** `school_data` table. |
| **Variables we use?** | Name (`name`/`schoolName`/`title`), level (`schoolLevels` etc.), coordinates (`latitude`/`longitude` etc.), and in import script only: `rating`/`schoolRating`. |

---

## 11. Related Files

| File | Role |
|------|------|
| **`backend/apify_client.py`** | `ApifySchoolClient`: `get_schools_by_bounds()`, `get_schools_by_address()`, `_find_closest_school()`, actor run and result fetch. |
| **`config/config.py`** | `APIFY_API_TOKEN`, `APIFY_ZILLOW_SCHOOL_ACTOR_ID`. |
| **`backend/routes.py`** | Calls `ApifySchoolClient.get_schools_by_address()` in address lookup and in export; uses returned names to match `school_data`. |
| **`scripts/import_missing_schools.py`** | Calls Apify by bounds and writes/updates `school_data` (name, rating, level, lat/lng). |
| **`ADDRESS_TO_ZONED_SCHOOLS_WALKTHROUGH.md`** | Full flow; Apify = Layer 1. |
| **`DATA_SOURCES_AND_LINKS.md`** | Lists Apify and GreatSchools as data sources. |

---

## 12. Why “Apify Data” Isn’t a Single Dataset

- There is **no static “Apify dataset”** we download. Each run is a **new scrape** of GreatSchools/Zillow for the bounds we send.
- **Freshness:** Whatever was on the site at run time.
- **Consistency:** Field names can vary; we handle multiple variants (name, schoolName, title; schoolLevels array; latitude/longitude, etc.).
- **Persistence:** We only persist Apify-derived data when we run the **import** script and write to `school_data`. The rest of the time, Apify is a live lookup for **names** that we then join to our own `school_data` for ratings.

This is the full picture of how Apify data is utilized in your project.
