# Zip Code Boundary Coverage & How to Get More

## Current Status

When you search for an address, the system:
1. ✅ Loads school data
2. ✅ Loads census data  
3. ⚠️ **May not show zip code outline** if boundary data is missing

## How Much Boundary Data Do You Have?

Run this script to check your coverage:

```bash
python scripts/check_zip_boundary_coverage.py
```

This will show you:
- How many zip codes are in your database
- How many boundary files you have locally
- Which zip codes are missing boundaries
- Coverage percentage

## Why Boundaries Might Not Show

The zip code boundary outline may not appear when searching by address if:

1. **No local boundary file exists** - The zip code doesn't have a `.geojson` file in `data/zip_boundaries/`
2. **Online sources fail** - The system tries to fetch from Census TIGERweb, but it may timeout or fail
3. **Boundaries checkbox is off** - Make sure "Show Boundaries" is checked in the map controls

## How to Get More Zip Boundaries

### Option 1: Download All Missing Boundaries (Recommended)

This will download boundaries for ALL zip codes in your database that don't have local files:

```bash
python scripts/download_accurate_boundaries.py
```

**What it does:**
- Checks all zip codes in your database
- Downloads missing boundaries from Census TIGERweb (FREE, official source)
- Saves them to `data/zip_boundaries/`
- Shows progress and statistics

**Time estimate:** ~0.5 seconds per zip code (with 0.5s delay between requests)
- 100 zip codes: ~1 minute
- 1,000 zip codes: ~10 minutes
- 10,000 zip codes: ~1.5 hours

### Option 2: Download Specific Zip Codes

If you only need boundaries for specific zip codes:

```bash
python scripts/download_accurate_boundaries.py --zip-codes 28204 28205 28206
```

### Option 3: Download Boundaries for First N Zip Codes (Testing)

To test with a smaller batch:

```bash
python scripts/download_accurate_boundaries.py --limit 100
```

## Where Boundaries Come From

The system tries multiple sources (in order):

1. **Local files** (`data/zip_boundaries/{zip_code}.geojson`) - Fastest, most reliable
2. **Census TIGERweb API** - Official US Census Bureau source (FREE)
3. **OpenDataSoft API** - Public zip code boundaries
4. **GitHub CDN** - Pre-processed GeoJSON files
5. **Approximate boundary** - Rectangle/circle from geocoding (fallback)

## Fix Applied

I've fixed the code so that when you search by address:
- ✅ The "Show Boundaries" checkbox is automatically enabled
- ✅ The boundary polygon is always displayed (if available)
- ✅ Better error handling if boundary fetch fails

## Checking Your Coverage

After downloading boundaries, check your coverage again:

```bash
python scripts/check_zip_boundary_coverage.py
```

You should see improved coverage percentage.

## Total US Zip Codes

There are approximately **33,000-34,000** active zip codes in the US. If you have:
- **621 boundaries** = ~1.8% coverage
- **3,000 boundaries** = ~9% coverage  
- **10,000 boundaries** = ~30% coverage
- **33,000 boundaries** = ~100% coverage

## Next Steps

1. **Check your current coverage:**
   ```bash
   python scripts/check_zip_boundary_coverage.py
   ```

2. **Download missing boundaries:**
   ```bash
   python scripts/download_accurate_boundaries.py
   ```

3. **Test the fix:**
   - Search for an address
   - The zip code outline should now appear
   - If it doesn't, check the browser console for errors

## Troubleshooting

### Boundary Still Not Showing?

1. **Check browser console** - Look for errors when searching
2. **Verify boundary file exists:**
   ```bash
   ls data/zip_boundaries/28204.geojson  # Replace with your zip code
   ```
3. **Check "Show Boundaries" checkbox** - Should be automatically checked now
4. **Try a different zip code** - Some zip codes may not have boundaries available

### Download Fails?

- Census TIGERweb may be temporarily unavailable
- Try again later
- Check your internet connection
- Some zip codes may not exist in Census data (very rare)

## Notes

- All boundary downloads are **100% FREE** (from US Census Bureau)
- Boundaries are saved locally for fast access
- Once downloaded, boundaries work offline
- Boundaries are accurate ZCTA (Zip Code Tabulation Area) shapes from Census Bureau
