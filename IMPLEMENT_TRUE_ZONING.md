# Implementing True School Zoning

## Data Sources Available

### 1. NCES School Attendance Boundary Survey (SABS)
- **Years Available**: 2013-2014, 2015-2016
- **Format**: Shapefiles (need conversion to GeoJSON)
- **Coverage**: 70,000+ schools nationwide
- **Download**: https://nces.ed.gov/programs/edge/sabs
- **Note**: Data is a few years old but still useful

### 2. NCES EDGE API
- **Service**: ArcGIS REST API
- **Format**: GeoJSON, JSON, PBF
- **URL**: https://nces.ed.gov/opendata.arcgis.com
- **Coverage**: School district boundaries (not individual school zones)

### 3. State/District Specific
- Some districts have "Find Your School" tools
- Wake County (NC) has an API: https://osageo.wcpss.net

## Implementation Strategy

### Phase 1: Download and Process NCES Data

1. **Download SABS shapefiles** for NC and SC
2. **Convert to GeoJSON** 
3. **Match to our school database** (by name/location)
4. **Store in database** (PostGIS or GeoJSON column)

### Phase 2: Add Point-in-Polygon Logic

1. **Install PostGIS** (if using PostgreSQL) OR use `shapely` library
2. **Query schools** with attendance zones
3. **Test if address** falls within zone polygon
4. **Return zoned schools** (not just closest)

### Phase 3: Hybrid Approach

1. **Try zone-based lookup first** (if zone data available)
2. **Fallback to distance-based** (if no zone data)
3. **Best of both worlds**

## Recommended Approach: PostGIS

Since you're using PostgreSQL (Supabase), PostGIS is the best option:

### Advantages:
- ✅ Built-in spatial functions
- ✅ Fast spatial queries
- ✅ Point-in-polygon built-in
- ✅ Can store GeoJSON directly

### Implementation Steps:

1. **Enable PostGIS** in Supabase
2. **Add attendance_zone column** (geometry type)
3. **Import zone boundaries** from NCES
4. **Update query** to use `ST_Contains()` function
