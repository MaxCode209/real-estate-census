# Zip Code Boundary Implementation Note

## Current Status

The system attempts to fetch actual zip code boundary polygons from multiple sources:
1. Backend API (tries OpenDataSoft, Census TIGERweb, GitHub)
2. Direct CDN sources (GitHub repositories)
3. Falls back to approximate rectangles if exact boundaries aren't found

## Why You're Seeing Rectangles

If you're seeing rectangular boundaries, it means:
- The public APIs aren't returning data (SSL issues, rate limits, or data not available)
- The CDN sources don't have that specific zip code
- The system is falling back to approximate boundaries from geocoding

## Best Long-Term Solution

For production use with reliable actual boundaries, consider:

### Option 1: Google Data-Driven Styling (Recommended)
- Most reliable and always up-to-date
- Requires enabling Region Lookup API
- Uses Google's own boundary data

### Option 2: Download and Host ZCTA Boundaries
1. Download from Census Bureau: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
2. Convert shapefiles to GeoJSON
3. Host on your server/CDN
4. Serve via your API

### Option 3: Use Boundaries.io API
- Sign up for free API key
- Reliable service with good coverage
- Free tier available

## Testing

To test if boundaries are working:
1. Open browser console (F12)
2. Search for zip code 28204
3. Look for console messages about boundary fetching
4. Check Network tab to see API calls

If you see 404s or errors, the public sources aren't working for that zip code.

