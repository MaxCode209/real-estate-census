# GreatSchools API Analysis & School Selection Strategy

## Current Situation

### What We're Currently Using:
1. **NCES Attendance Zones** (point-in-polygon) - Fast, but may be outdated
2. **Apify/Zillow Scraper** - Gets data from GreatSchools/Zillow, but:
   - Takes 30-60 seconds per request
   - Costs Apify credits
   - Not guaranteed to match GreatSchools exactly
3. **Distance-based fallback** - Finds closest schools by proximity

### The Problem:
- Zoned schools may not match GreatSchools.com exactly
- School selection logic after zoned schools doesn't mirror GreatSchools

---

## GreatSchools API Options

### Option 1: NearbySchools™ API
**Cost:** $52.50-$97.50/month  
**What it provides:**
- ✅ School name, address, type, grades
- ✅ NCES and state IDs
- ✅ School website URLs
- ✅ GreatSchools profile links
- ✅ School Rating Bands (in higher tier)
- ❌ **NO 1-10 Ratings** (only rating bands)
- ❌ **NO Zoned School Data** (not included)

**Limitation:** Does NOT provide zoned school information or detailed ratings.

### Option 2: Enterprise Data Licensing
**Cost:** Custom pricing (likely expensive)  
**What it provides:**
- ✅ Full 1-10 ratings
- ✅ **School Assignment & District Boundary data** (zoned schools)
- ✅ Complete school database

**Best for:** Large-scale commercial applications

---

## Benefits of Using GreatSchools API

### If We Use NearbySchools™ API ($52.50/month):

**Pros:**
1. ✅ **Official data source** - Direct from GreatSchools
2. ✅ **Reliable and up-to-date** - No scraping delays
3. ✅ **Consistent data format** - Predictable structure
4. ✅ **No rate limiting issues** - Official API access
5. ✅ **15,000 calls/month** - Good for moderate usage
6. ✅ **14-day free trial** - Test before committing

**Cons:**
1. ❌ **No zoned school data** - Still need to determine zones separately
2. ❌ **No 1-10 ratings** - Only rating bands (e.g., "Above Average")
3. ❌ **Monthly cost** - $52.50-$97.50/month
4. ❌ **Still need another solution** - For zoned schools

### If We Use Enterprise Licensing:

**Pros:**
1. ✅ **Complete solution** - Zoned schools + ratings
2. ✅ **Most accurate** - Official GreatSchools data
3. ✅ **No scraping needed** - Direct API access

**Cons:**
1. ❌ **Very expensive** - Likely thousands per month
2. ❌ **Enterprise sales process** - May take time to set up
3. ❌ **May be overkill** - For a single-user or small team

---

## Recommended Approach: Mirror GreatSchools Logic

Since GreatSchools API doesn't provide zoned schools in the affordable tier, **we should improve our current approach** to mirror GreatSchools' logic:

### Step 1: Improve Zoned School Detection

**Current Issues:**
- NCES attendance zones may be outdated
- Apify scraping is slow and may not match exactly

**Solutions:**

#### A. Prioritize Apify/GreatSchools Scraping (Recommended)
- **Why:** Apify gets data directly from GreatSchools/Zillow
- **Action:** Make Apify the PRIMARY source, not fallback
- **Trade-off:** Slower (30-60 sec) but more accurate

#### B. Use GreatSchools Website Scraping
- **Why:** Direct access to what users see on GreatSchools.com
- **Action:** Scrape the address lookup page directly
- **Trade-off:** May break if website changes

#### C. Cache Zoned Schools
- **Why:** Once we know zoned schools for an address, cache them
- **Action:** Store in database: `address -> zoned_schools`
- **Benefit:** Fast lookups for repeat addresses

### Step 2: Mirror GreatSchools' School Selection Logic

**What GreatSchools Shows After Zoned Schools:**

Based on GreatSchools.com behavior, after showing the 3 zoned schools, they typically show:

1. **Top-rated schools nearby** (sorted by rating, then distance)
2. **Within reasonable distance** (typically 5-10 miles)
3. **All school types** (Elementary, Middle, High combined)
4. **Public schools prioritized** (may include charter, rarely private)
5. **Rated schools only** (excludes unrated schools)

**Current Implementation:**
- ✅ Gets top 10 schools by proximity
- ✅ Sorts by rating (descending), then distance
- ✅ Includes all types
- ❌ Doesn't filter by school type (public/charter/private)
- ❌ Doesn't limit distance (uses 10 miles, but GreatSchools may use less)

**Recommended Changes:**

```python
# Mirror GreatSchools logic:
1. Zoned schools first (Elementary, Middle, High) - DONE ✅
2. Additional schools sorted by:
   - Rating (highest first) - DONE ✅
   - Distance (closest first) - DONE ✅
   - Filter: Public schools only (or public + charter)
   - Filter: Within 5-7 miles (not 10)
   - Filter: Rated schools only (exclude unrated)
   - Limit: 10 total schools
```

---

## Implementation Plan

### Phase 1: Improve Zoned School Accuracy (Priority 1)

1. **Make Apify primary source** for zoned schools
   - Remove attendance zone dependency (or make it fallback)
   - Use Apify first, then fall back to zones if Apify fails

2. **Add caching layer**
   - Cache zoned schools by address/coordinates
   - Store in database: `cached_zoned_schools` table
   - TTL: 6 months (zones don't change often)

3. **Add GreatSchools direct scraping** (optional)
   - As backup to Apify
   - Scrape address lookup page directly

### Phase 2: Mirror GreatSchools Selection Logic (Priority 2)

1. **Update school filtering:**
   ```python
   # Filter additional schools:
   - School type: Public or Charter (exclude private)
   - Distance: Within 5-7 miles (not 10)
   - Rating: Must have rating (exclude unrated)
   - Sort: Rating (desc) → Distance (asc)
   ```

2. **Add school type filtering:**
   - Check if school is public/charter/private
   - Filter out private schools (unless user requests them)

3. **Adjust distance radius:**
   - Reduce from 10 miles to 5-7 miles
   - More aligned with GreatSchools behavior

### Phase 3: Consider GreatSchools API (Optional)

**If budget allows ($52.50/month):**
- Use NearbySchools™ API for:
  - School details (address, website, etc.)
  - School type verification
  - Rating bands (if needed)
- **Still use Apify for zoned schools** (API doesn't provide this)

**If budget is larger:**
- Consider Enterprise licensing for complete solution
- Get zoned schools + ratings from one source

---

## Cost Comparison

| Solution | Monthly Cost | Zoned Schools | Ratings | Speed |
|----------|-------------|--------------|---------|-------|
| **Current (Apify)** | ~$10-50 | ✅ Yes | ✅ Yes | ⚠️ Slow (30-60s) |
| **NearbySchools API** | $52.50 | ❌ No | ⚠️ Bands only | ✅ Fast |
| **Enterprise API** | $$$$ | ✅ Yes | ✅ Yes | ✅ Fast |
| **Improved Current** | ~$10-50 | ✅ Yes | ✅ Yes | ⚠️ Slow (but cached) |

---

## Recommendation

**For now: Improve current approach (Phase 1 & 2):**

1. ✅ **Make Apify primary** for zoned schools
2. ✅ **Add caching** to speed up repeat lookups
3. ✅ **Update selection logic** to match GreatSchools (filter by type, distance, rating)
4. ⏸️ **Monitor costs** - If Apify costs get high, consider API

**Later (if needed):**
- If Apify costs exceed $50/month → Consider NearbySchools API
- If accuracy is critical → Consider Enterprise licensing

---

## Next Steps

1. **Update export_report function** to:
   - Filter additional schools by type (public/charter only)
   - Reduce distance to 5-7 miles
   - Exclude unrated schools

2. **Update get_schools_by_address** to:
   - Prioritize Apify over attendance zones
   - Add caching for zoned schools

3. **Test with real addresses** to verify matches GreatSchools.com
