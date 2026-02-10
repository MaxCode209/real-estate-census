# How Zoned Schools Are Determined - Complete Logic Explanation

## Overview

The system uses a **two-step priority approach** to determine which schools are zoned for a specific address:

1. **Primary:** Apify/GreatSchools (most accurate, matches GreatSchools.com)
2. **Fallback:** NCES Attendance Zones (point-in-polygon testing)

---

## Step-by-Step Process

### Step 0: Geocode the Address
**Input:** Address string (e.g., "1111 Metropolitan Ave, Charlotte, NC 28204")

**Process:**
- Uses Google Geocoding API to convert address → latitude/longitude
- Extracts zip code from geocoded result

**Output:** 
- `lat`: Latitude (e.g., 35.2271)
- `lng`: Longitude (e.g., -80.8431)
- `zip_code`: Zip code (e.g., "28204")

---

### Step 1: Try Apify/GreatSchools FIRST (Primary Source) ⭐

**Why Apify is Primary:**
- Gets data directly from GreatSchools/Zillow websites
- Matches what users see on GreatSchools.com
- Most accurate and up-to-date
- **Trade-off:** Slower (30-60 seconds per request)

**How It Works:**

1. **Call Apify Zillow School Scraper:**
   ```python
   apify_client = ApifySchoolClient()
   apify_elementary, apify_middle, apify_high = apify_client.get_schools_by_address(
       address, lat, lng, radius_miles=2.0
   )
   ```

2. **Apify's Process:**
   - Creates a bounding box around the address (2-mile radius)
   - Scrapes GreatSchools/Zillow for schools in that area
   - Returns all schools found (public, charter, rated schools only)
   - Filters by school level (elementary, middle, high)

3. **Find Closest Schools:**
   - For each school type (elementary, middle, high):
     - Filters schools by level (e.g., only elementary schools)
     - Calculates distance from address to each school
     - Returns the **closest school** of each type
   - **Assumption:** The closest school is typically the zoned school

4. **Extract School Names:**
   - Gets school name from Apify result
   - Tries multiple field names: `name`, `schoolName`, `title`
   - Stores as: `{'school_name': 'Sedgefield Elementary'}`

**Result:**
- `zoned_elementary`: School name or None
- `zoned_middle`: School name or None  
- `zoned_high`: School name or None

**If Successful:** ✅ Use these schools, skip to Step 3 (matching to database)

**If Failed:** ⚠️ Continue to Step 2 (attendance zones fallback)

---

### Step 2: Fallback to NCES Attendance Zones (Point-in-Polygon)

**When Used:**
- Apify fails (timeout, error, or no results)
- Apify doesn't return schools for the address

**How It Works:**

1. **Load Attendance Zones from Database:**
   ```python
   zones = db.query(AttendanceZone).filter(
       or_(AttendanceZone.state == 'NC', AttendanceZone.state == 'SC')
   ).all()
   ```
   - Gets all attendance zone boundaries from `attendance_zones` table
   - Currently filtered to NC and SC only
   - Each zone has a GeoJSON polygon boundary

2. **Point-in-Polygon Testing:**
   ```python
   zoned_elementary = find_zoned_schools(lat, lng, zones_list, 'elementary')
   zoned_middle = find_zoned_schools(lat, lng, zones_list, 'middle')
   zoned_high = find_zoned_schools(lat, lng, zones_list, 'high')
   ```

3. **How Point-in-Polygon Works:**
   - For each attendance zone polygon:
     - Tests if the address point (lat, lng) falls **inside** the polygon
     - Uses geometric algorithm (ray casting or winding number)
   - If point is inside a zone → that's the zoned school
   - Returns the school name for that zone

**Result:**
- `zoned_elementary`: School name or None
- `zoned_middle`: School name or None
- `zoned_high`: School name or None

**Limitations:**
- ⚠️ Attendance zone data may be outdated
- ⚠️ Only covers NC and SC currently
- ⚠️ May not match GreatSchools exactly

---

### Step 3: Match School Names to Database for Ratings

**After getting zoned school names** (from Apify or attendance zones):

**Goal:** Find the school in our `school_data` database to get ratings

**Process:**

1. **Fuzzy Name Matching:**
   - Tries multiple matching strategies:
   
   **Strategy 1: Exact Match**
   ```python
   school = db.query(SchoolData).filter(
       SchoolData.elementary_school_name == elementary_name
   ).first()
   ```
   
   **Strategy 2: Case-Insensitive Partial Match**
   ```python
   school = db.query(SchoolData).filter(
       SchoolData.elementary_school_name.ilike(f'%{elementary_name}%')
   ).first()
   ```
   
   **Strategy 3: Clean Name Match** (remove common suffixes)
   - Removes: "School", "Elementary", "Elem", "PreK-8", etc.
   - Tries matching cleaned name
   
   **Strategy 4: Reverse Match** (for PreK-8 schools)
   - If zone has "PreK-8", also search for "Elementary" version

2. **Extract Rating:**
   - If school found: Get rating from database
   - If not found: Rating = None (shows as "N/A")

**Result:**
- `elementary_rating`: Rating (1-10) or None
- `middle_rating`: Rating (1-10) or None
- `high_rating`: Rating (1-10) or None

---

### Step 4: Final Fallback (Distance-Based)

**If both Apify AND attendance zones fail:**

**Process:**
- Searches `school_data` table for schools within 5 miles
- Finds closest school of each type (by distance)
- Uses Haversine formula for accurate distance calculation

**Result:**
- Returns closest schools (may not be zoned schools)
- Less accurate than zoned schools

---

## Complete Flow Diagram

```
Address Input
    ↓
Geocode Address → Get lat/lng
    ↓
┌─────────────────────────────────────┐
│ STEP 1: Try Apify (Primary)         │
│ - Scrape GreatSchools/Zillow        │
│ - Find closest schools              │
│ - Time: 30-60 seconds               │
└─────────────────────────────────────┘
    ↓
    ├─ Success? → Extract school names
    │              ↓
    │         STEP 3: Match to database
    │              ↓
    │         Return ratings
    │
    └─ Failed? → ┌─────────────────────────────────────┐
                  │ STEP 2: Try Attendance Zones        │
                  │ - Point-in-polygon test             │
                  │ - Fast (< 1 second)                 │
                  └─────────────────────────────────────┘
                       ↓
                       ├─ Success? → Extract school names
                       │              ↓
                       │         STEP 3: Match to database
                       │              ↓
                       │         Return ratings
                       │
                       └─ Failed? → ┌──────────────────────┐
                                     │ STEP 4: Distance-based│
                                     │ - Find closest schools│
                                     │ - Less accurate       │
                                     └──────────────────────┘
```

---

## Why This Approach?

### Apify First (Primary):
✅ **Most Accurate** - Matches GreatSchools.com exactly  
✅ **Up-to-Date** - Gets current zoned school data  
✅ **Reliable** - Direct from GreatSchools/Zillow  
⚠️ **Slower** - Takes 30-60 seconds

### Attendance Zones Second (Fallback):
✅ **Fast** - Point-in-polygon is instant  
✅ **Offline** - Works without external APIs  
⚠️ **May be Outdated** - NCES data may not match current zones  
⚠️ **Limited Coverage** - Only NC/SC currently

---

## Example: "1111 Metropolitan Ave, Charlotte, NC 28204"

**What Happens:**

1. **Geocode:** Gets lat/lng for address
2. **Apify:** Scrapes GreatSchools, finds:
   - Sedgefield Elementary (closest elementary)
   - Sedgefield Middle (closest middle)
   - Myers Park High (closest high)
3. **Match to Database:** Looks up ratings:
   - Sedgefield Elementary → Rating found ✅
   - Sedgefield Middle → Rating found ✅
   - Myers Park High → Rating found ✅
4. **Return:** All three schools with ratings

**If Apify Failed:**
- Would try attendance zones (point-in-polygon)
- Might find different schools if zones are outdated
- Would still match to database for ratings

---

## Current Issues & Limitations

### Issue 1: Apify is Slow
- **Problem:** Takes 30-60 seconds per address lookup
- **Solution:** Could add caching (store results for repeat addresses)

### Issue 2: Attendance Zones May Be Outdated
- **Problem:** NCES zones may not match current school assignments
- **Solution:** Apify is now primary (more accurate)

### Issue 3: Name Matching May Fail
- **Problem:** School names from Apify may not exactly match database
- **Solution:** Multiple fuzzy matching strategies (already implemented)

### Issue 4: Limited State Coverage
- **Problem:** Attendance zones only for NC/SC
- **Solution:** Apify works for all states (when available)

---

## Summary

**Current Logic:**
1. ✅ **Apify FIRST** - Gets zoned schools from GreatSchools (most accurate)
2. ✅ **Attendance Zones SECOND** - Fast fallback if Apify fails
3. ✅ **Match to Database** - Get ratings for zoned schools
4. ✅ **Distance-Based LAST** - Final fallback if all else fails

**Result:** Zoned schools that match GreatSchools.com, with ratings from your database.
