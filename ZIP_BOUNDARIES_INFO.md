# Zip Code Boundary Polygons

## Current Implementation

The application now attempts to fetch **actual zip code boundary polygons** (GeoJSON) instead of approximate rectangles/circles.

## How It Works

1. **Primary Source**: Tries to fetch from OpenDataSoft API (public US zip code boundaries)
2. **Fallback Sources**: 
   - GitHub repositories with state-based zip code GeoJSON
   - ZCTA5 format boundaries
3. **Final Fallback**: If no exact boundary is found, uses approximate boundary from Google Geocoding

## Data Sources

### OpenDataSoft (Primary)
- **URL**: `https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/us-zip-code-labels-and-boundaries`
- **Format**: GeoJSON
- **Coverage**: All US zip codes
- **Free**: Yes

### GitHub Repositories (Fallback)
- Various repositories with pre-processed zip code boundaries
- State-based organization
- Free and open source

## Improving Boundary Accuracy

### Option 1: Use Census Bureau TIGER/Line Files (Most Accurate)
1. Download ZCTA boundaries from Census Bureau
2. Convert shapefiles to GeoJSON
3. Host locally or on a CDN
4. Update the API endpoint to serve from local source

### Option 2: Use a Commercial Service
- Services like Mapbox, HERE, or Esri provide zip code boundaries
- Usually requires API key and may have costs

### Option 3: Pre-process and Store
1. Download all ZCTA boundaries
2. Store in your database or file system
3. Serve via your API

## Current Status

- ✅ Attempts to fetch actual boundaries
- ✅ Falls back gracefully to approximate boundaries
- ✅ Works for zip codes with available GeoJSON data
- ⚠️ Some zip codes may still show approximate boundaries if GeoJSON not available

## Testing

Try searching for zip codes like:
- `10001` (Manhattan, NY) - Should show actual boundary
- `90210` (Beverly Hills, CA) - Should show actual boundary
- `28204` (Charlotte, NC) - Should show actual boundary

If a zip code shows a rectangle/circle instead of the actual shape, it means the GeoJSON wasn't found and it's using the approximate boundary.

