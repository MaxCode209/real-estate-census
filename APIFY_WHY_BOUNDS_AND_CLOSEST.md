# Why We Use a 2-Mile Radius and “Closest” Instead of “Address → 3 Zoned Schools”

## The Question

Why do we create a 2-mile radius and pick the **closest** school of each level, instead of just entering the address and pulling in the **3 zoned schools** for that address? Zillow (and GreatSchools) show the assigned schools for an address—and those aren’t always the closest by distance.

## Short Answer

**We’d prefer “address in → 3 zoned schools out.”** We can’t do that with the current Apify actor because it **only accepts a bounding box** (north/south/east/west), not an address. It returns **all schools in that area**, not “the 3 zoned schools for this address.” So we approximate by using a ~2-mile box and picking the **closest** elementary, middle, and high—which can be wrong when the true zoned school is farther away.

## Why the Actor Works This Way

The Apify actor we use is **Zillow School Scraper** (`axlymxp/zillow-school-scraper`). From Apify’s docs and input schema:

- **Input:** Geographic boundaries only — `eastLongitude`, `westLongitude`, `northLatitude`, `southLatitude` (plus filters like min rating, school level, etc.).
- **Output:** A list of schools that fall **within that box** (name, level, rating, coordinates, etc.).

There is **no input** for “address” or “property ID” that would return “the 3 zoned schools for this address.” The actor is built for “give me a region → I’ll return all schools in that region,” not “give me an address → I’ll return the zoned schools for that address.”

So we have no way, with this actor alone, to replicate Zillow’s “enter address → see assigned elementary, middle, high.”

## What We Do Instead (and Why It’s a Compromise)

1. **Geocode** the user’s address → get (lat, lng).
2. **Build a ~2-mile bounding box** around (lat, lng).
3. **Call the actor** with that box → get back **all schools in that area**.
4. **Pick the closest** school of each level (elementary, middle, high) by distance to (lat, lng).
5. Use those **names** and match to our `school_data` for ratings.

So “closest” is a **proxy** for “zoned.” It’s right when the zoned school happens to be the closest in the box; it’s wrong when the zoned school is farther away than another school in the area (e.g. a charter or private school nearby, or a different attendance zone boundary).

**Why 2 miles?** A practical choice: large enough to usually include the zoned schools, small enough to limit result count and Apify cost. It doesn’t fix the “zoned ≠ closest” issue.

## What Would Be Better

Ideally we’d have one of:

1. **An Apify actor (or API) that accepts an address** (or lat/lng) and returns **the 3 zoned schools** for that address—like Zillow’s UI. Then we’d send the address and use those 3 names directly, no radius, no “closest.”
2. **A change to the current actor** — e.g. the maintainer adds an “address” or “property” input that calls whatever Zillow/GreatSchools endpoint returns zoned schools for that address, if such an endpoint exists.
3. **A different scraper** — e.g. one that, given an address, loads the Zillow (or GreatSchools) page for that address and extracts the 3 assigned schools from the page.

Until then, we keep “2-mile box + closest” and treat it as a known limitation. Our **NCES attendance zones** fallback (point-in-polygon) is true zoning by geography but only for NC/SC and 2015–2016 data; it doesn’t replace “address → 3 zoned schools” from Zillow/GreatSchools.

## Summary

| What we want | Address in → 3 zoned schools (elementary, middle, high) — like Zillow. |
|--------------|-----------------------------------------------------------------------|
| What the actor supports | Bounding box in → all schools in that area.                          |
| What we do | ~2-mile box + pick **closest** of each level (proxy for zoned).       |
| Why it can be wrong | Zoned school ≠ always the closest school in the box.                 |

So: we use a 2-mile radius and “closest” **because the Apify actor doesn’t support “address → zoned schools.”** If we could enter the address and get the 3 zoned schools directly, we would.
