# How to Identify Zoned Schools for Each Address

## Current Approach (Distance-Based)

**What we're doing now:**
- Finding the **nearest** elementary, middle, and high schools by distance
- Using SQL distance calculation: `SQRT(POWER(latitude - :lat, 2) + POWER(longitude - :lng, 2))`
- Search radius: ~2 miles from the address
- Returns the closest school of each type

**Limitations:**
- ❌ Not true "zoned" schools - just closest by distance
- ❌ Doesn't account for school attendance boundaries
- ❌ May return wrong school if boundaries are irregular
- ❌ Doesn't handle school choice, magnets, or special programs

## True School Zoning (What You're Asking About)

### The Challenge

**School zoning is based on:**
1. **Geographic boundaries** (attendance zones) - polygon shapes
2. **Address-based assignment** - specific street addresses assigned to schools
3. **Sometimes distance-based** - but with specific boundary rules

### What We'd Need

#### Option 1: School Attendance Zone Boundaries (Most Accurate)

**Requirements:**
1. **School attendance zone polygons** (GeoJSON/Shapefiles)
   - Each school has a boundary polygon
   - Address falls within the polygon = that's the zoned school
   
2. **Point-in-polygon testing**
   - Check if address coordinates fall within each school's boundary
   - Use libraries like `shapely` (Python) or `turf.js` (JavaScript)

3. **Data source for boundaries**
   - **NCES (National Center for Education Statistics)**: Has some attendance zone data
   - **State education departments**: Often publish attendance zone maps
   - **Commercial services**: SchoolDigger, GreatSchools (may require API access)
   - **OpenStreetMap**: Some attendance zones mapped by volunteers

**Implementation:**
```python
# Pseudo-code
def find_zoned_schools(address_lat, address_lng):
    zoned_schools = {
        'elementary': None,
        'middle': None,
        'high': None
    }
    
    # For each school in database
    for school in all_schools:
        # Check if address is within school's attendance zone polygon
        if point_in_polygon(address_lat, address_lng, school.attendance_zone):
            if school.level == 'elementary' and not zoned_schools['elementary']:
                zoned_schools['elementary'] = school
            # ... same for middle and high
    
    return zoned_schools
```

**Complexity:** High
- Need to acquire/store attendance zone boundaries
- Need point-in-polygon geometry library
- Boundaries change annually (maintenance required)

#### Option 2: Address-to-School Lookup Tables

**Requirements:**
1. **Address-to-school mapping database**
   - Each address → assigned elementary/middle/high school
   - Could be from school district websites or APIs

2. **Address normalization**
   - Standardize address formats for matching
   - Handle variations (St vs Street, etc.)

**Implementation:**
```python
# Pseudo-code
def find_zoned_schools(normalized_address):
    # Lookup in address-to-school mapping table
    assignment = address_school_map.get(normalized_address)
    
    if assignment:
        return {
            'elementary': assignment.elementary_school_id,
            'middle': assignment.middle_school_id,
            'high': assignment.high_school_id
        }
    return None
```

**Complexity:** Medium
- Need to acquire address-to-school mappings
- Address normalization can be tricky
- Data may not be publicly available for all districts

#### Option 3: School District APIs

**Some districts provide APIs:**
- School district websites with "Find Your School" tools
- Some have APIs or data exports
- Varies by district

**Complexity:** Very High
- Different API for each district
- Inconsistent data formats
- Many districts don't have APIs
- Would need to integrate with 100+ different systems

## Recommended Approach: Hybrid

### Phase 1: Enhanced Distance-Based (Current + Improvements)

**Improvements we can make now:**
1. **Larger search radius** - increase from 2 miles to 5-10 miles
2. **Multiple candidates** - return top 3 closest, let user see options
3. **School district filtering** - if we know the district, filter by it
4. **Better distance calculation** - use Haversine formula for accurate miles

**Code example:**
```python
from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles between two points."""
    R = 3959  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c
```

### Phase 2: Add Attendance Zone Data (When Available)

**For NC and SC specifically:**
1. **Check NCES** - They have some attendance zone data
2. **State education departments** - May publish zone maps
3. **School district websites** - Many have "Find Your School" tools we could scrape/API

**If we get zone boundaries:**
- Store as GeoJSON polygons in database
- Use PostGIS (PostgreSQL extension) for spatial queries
- Query: `SELECT * FROM schools WHERE ST_Contains(attendance_zone, ST_Point(lng, lat))`

## Current Database Schema

**What we have:**
```sql
school_data:
  - latitude, longitude (school location)
  - elementary_school_name, rating, address
  - middle_school_name, rating, address
  - high_school_name, rating, address
```

**What we'd need to add:**
```sql
school_data:
  - attendance_zone (GeoJSON polygon) -- NEW
  - school_district_name -- NEW
  - school_district_id -- NEW
```

## Practical Recommendation

### Short Term (Now):
✅ **Keep current distance-based approach** - it works for most cases
✅ **Improve distance calculation** - use Haversine formula
✅ **Add school district info** - if available in Apify data
✅ **Return multiple candidates** - show top 3 closest schools

### Medium Term (Next Phase):
1. **Research attendance zone data sources** for NC/SC
2. **Acquire zone boundaries** where available
3. **Add point-in-polygon logic** for addresses with zone data
4. **Fallback to distance** when zone data unavailable

### Long Term (If Needed):
1. **Build zone boundary database** from multiple sources
2. **Maintain annual updates** (zones change)
3. **Add district-specific APIs** where available

## Data Sources to Explore

### Free/Open Sources:
- **NCES School Attendance Boundaries**: https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries
- **OpenStreetMap**: Some attendance zones mapped
- **State education department websites**: Often have zone maps

### Commercial Sources:
- **SchoolDigger API**: May have zone data
- **GreatSchools API**: May have zone information
- **Esri Education Data**: Commercial but comprehensive

## Bottom Line

**Current approach (distance-based):**
- ✅ Works now with existing data
- ✅ Fast and simple
- ✅ Good enough for most use cases
- ❌ Not 100% accurate for true zoning

**True zoning approach:**
- ✅ More accurate
- ❌ Requires additional data (attendance zone boundaries)
- ❌ More complex implementation
- ❌ Ongoing maintenance (zones change annually)

**Recommendation:** Start with improved distance-based, then add true zoning as data becomes available.
