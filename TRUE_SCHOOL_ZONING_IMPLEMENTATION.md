# True School Zoning Implementation Guide

## Overview

The system now supports **true school zoning** using attendance zone boundaries. When zone data is available, it uses point-in-polygon testing to find the actual zoned schools. When zone data is not available, it falls back to distance-based lookup.

## How It Works

### 1. Zone-Based Lookup (When Available)
- Checks if address coordinates fall within school attendance zone polygons
- Uses point-in-polygon geometry testing
- Returns the **actual zoned school** (not just closest)

### 2. Distance-Based Fallback
- If no zone data available, uses distance-based lookup
- Finds nearest schools within 5 miles
- Uses Haversine formula for accurate distance

## Database Schema

### New Table: `attendance_zones`
```sql
- id (primary key)
- school_id (foreign key to school_data)
- school_name
- school_level ('elementary', 'middle', 'high')
- school_district
- state ('NC', 'SC')
- zone_boundary (GeoJSON text)
- data_year
- source ('NCES', 'district', etc.)
```

## Data Sources

### Option 1: NCES School Attendance Boundary Survey (SABS)
- **URL**: https://nces.ed.gov/programs/edge/sabs
- **Years**: 2013-2014, 2015-2016
- **Format**: Shapefiles (need conversion to GeoJSON)
- **Coverage**: 70,000+ schools nationwide
- **Cost**: FREE

### Option 2: NCES EDGE API
- **URL**: https://nces.ed.gov/opendata.arcgis.com
- **Format**: GeoJSON via REST API
- **Coverage**: School district boundaries (not individual school zones)
- **Cost**: FREE

### Option 3: District-Specific APIs
- Some districts have "Find Your School" tools
- Wake County (NC): https://osageo.wcpss.net
- Varies by district

## Implementation Steps

### Step 1: Install Dependencies
```bash
pip install shapely==2.0.2
```

### Step 2: Initialize Database
The new `attendance_zones` table will be created automatically when you run:
```bash
python scripts/init_db.py
```

### Step 3: Import Attendance Zone Data

#### Option A: Download NCES SABS Data
1. Go to: https://nces.ed.gov/programs/edge/sabs
2. Download shapefiles for 2015-2016 (most recent)
3. Extract and convert to GeoJSON
4. Run import script (see below)

#### Option B: Use Import Script
A script will be created to:
- Download NCES data
- Convert shapefiles to GeoJSON
- Match zones to schools in database
- Import into `attendance_zones` table

### Step 4: Test
1. Search an address with zone data
2. System will use point-in-polygon to find zoned schools
3. Falls back to distance if no zones found

## Current Status

✅ **Code Implementation**: Complete
- Zone-based lookup logic added
- Point-in-polygon testing with shapely
- Fallback to distance-based
- Database model created

⏳ **Data Import**: Pending
- Need to download NCES data
- Need to convert shapefiles to GeoJSON
- Need to match zones to schools
- Need to import into database

## Next Steps

1. **Download NCES SABS data** for NC and SC
2. **Convert shapefiles to GeoJSON**
3. **Match zones to schools** in database (by name/location)
4. **Import into database**
5. **Test with addresses**

## Benefits

- ✅ **More Accurate**: Returns actual zoned schools, not just closest
- ✅ **Handles Irregular Boundaries**: Works even if closest school isn't zoned
- ✅ **Backward Compatible**: Falls back to distance when zones unavailable
- ✅ **No Breaking Changes**: Existing functionality still works

## Technical Details

### Point-in-Polygon Testing
- Uses `shapely` library
- Converts GeoJSON to shapely Polygon
- Tests if Point(lng, lat) is within polygon
- Handles MultiPolygon geometries

### Performance
- Zone lookup: O(n) where n = number of zones
- Optimized with spatial indexes (when PostGIS available)
- Fast enough for real-time lookups

## Future Enhancements

1. **PostGIS Integration**: Use spatial indexes for faster queries
2. **Zone Caching**: Cache zone lookups for common addresses
3. **Multiple Zone Sources**: Combine NCES + district-specific data
4. **Zone Updates**: Annual updates as boundaries change
