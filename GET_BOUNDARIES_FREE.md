# Get FREE Zip Code Boundaries - Simple Guide

## The Easiest FREE Solution

Since free APIs are unreliable, here's the **simplest free approach**:

### Step 1: Download Boundaries (One-Time Setup)

**Option A: Use Mapshaper (Easiest - No Installation)**

1. Go to: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
2. Find "ZIP Code Tabulation Areas (ZCTAs)" 
3. Download the shapefile (e.g., `tl_2023_us_zcta520.zip`)
4. Go to: https://mapshaper.org/ (free, no signup)
5. Drag and drop the zip file onto mapshaper
6. In the console, type: `filter 'ZCTA5CE10 == "28204"'` (replace with your zip code)
7. Click "Export" → "GeoJSON"
8. Save as: `data/zip_boundaries/28204.geojson`

**Option B: Use QGIS (Free Desktop Software)**

1. Download QGIS: https://qgis.org/ (free)
2. Download Census ZCTA shapefile (same as above)
3. Open shapefile in QGIS
4. Filter by zip code
5. Export as GeoJSON
6. Save to: `data/zip_boundaries/{zip_code}.geojson`

### Step 2: That's It!

Once you have boundaries in `data/zip_boundaries/`, the app will automatically use them!

## Quick Script to Download Specific Zip Codes

I can create a script that downloads boundaries for just the zip codes you need (from your database). This is faster than downloading all 33,000+ zip codes.

Would you like me to:
1. Create a script to download boundaries for your existing 1,224 zip codes?
2. Or provide a simpler manual process?

## Current Status

The system is already set up to:
- ✅ Check for local boundaries first (fastest)
- ✅ Try free APIs as backup
- ✅ Use approximate boundaries if nothing found

**You just need to get the boundaries into the `data/zip_boundaries/` folder!**

