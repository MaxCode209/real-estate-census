# How to Get Accurate Zip Code Boundaries

## The Problem
Free APIs are unreliable and timing out, causing the map to show rectangles instead of actual zip code shapes.

## The Solution: Download from Census TIGERweb (FREE & OFFICIAL)

The **Census Bureau TIGERweb** is the official source for ZCTA (Zip Code Tabulation Area) boundaries. It's free and accurate.

## Quick Start

### Option 1: Download All Your Zip Codes (Recommended)

```bash
python scripts/download_accurate_boundaries.py
```

This will:
- Download boundaries for all 1,224 zip codes in your database
- Save them to `data/zip_boundaries/`
- Take about 10-15 minutes (with rate limiting)

### Option 2: Download Specific Zip Codes

```bash
python scripts/download_accurate_boundaries.py --zip-codes 28204 10001 90210
```

### Option 3: Test with a Few First

```bash
python scripts/download_accurate_boundaries.py --limit 10
```

## How It Works

1. **Script connects to Census TIGERweb** (official government source)
2. **Downloads GeoJSON boundaries** for each zip code
3. **Saves locally** to `data/zip_boundaries/{zip_code}.geojson`
4. **Map automatically uses them** - no code changes needed!

## After Downloading

1. **Refresh your browser** at http://localhost:5000
2. **Search for a zip code** (e.g., `28204`)
3. **You'll see the accurate boundary** with red border showing the exact shape!

## Alternative Options (If Census Fails)

### Option A: Boundaries.io (Free Tier)
1. Sign up: https://boundaries.io/
2. Get free API key
3. Add to `.env`: `BOUNDARIES_IO_API_KEY=your_key`
4. I can update the code to use it

### Option B: Download Census Shapefiles Manually
1. Go to: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
2. Download ZCTA shapefile
3. Use Mapshaper (mapshaper.org) to convert to GeoJSON
4. Extract individual zip codes

### Option C: Commercial Services
- **Mapbox**: Requires API key, may have costs
- **HERE Maps**: Requires API key
- **Esri**: Requires account

## Current Status

- ✅ Script ready to download from Census TIGERweb
- ✅ Code already checks local files first (fastest)
- ✅ Falls back to approximate if not found
- ⚠️ Need to run download script to get boundaries

## Next Steps

**Run the download script now:**
```bash
python scripts/download_accurate_boundaries.py
```

This will give you accurate boundaries for all your zip codes!
