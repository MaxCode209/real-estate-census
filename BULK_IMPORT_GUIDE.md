# Bulk School Data Import Guide

## Overview

Instead of calling Apify on every address search (which takes 30-60 seconds), we'll bulk import school data for major metro areas once, then do instant database lookups.

## Benefits

✅ **Instant Results** - No 30-60 second wait  
✅ **More Reliable** - No API timeouts  
✅ **Better UX** - Fast, responsive searches  
✅ **One-time Cost** - Import once, use forever  

## How It Works

1. **Bulk Import**: Run script to import schools for major metro areas
2. **Fast Lookup**: Route finds nearest schools from database (instant)
3. **Coverage**: Start with 20 major metros, expand as needed

## Running the Import

### Step 1: Run the Bulk Import Script

```bash
python scripts/bulk_import_schools.py
```

This will:
- Import schools for 20 major US metro areas
- Take 1-2 hours (30-60 seconds per metro × 20 metros)
- Store all schools in your database
- Cost: ~$0.40 per metro = ~$8 total for 20 metros

### Step 2: Test the Import

After import completes, try searching for an address in one of the imported metros. School scores should appear instantly!

## Current Metro Coverage

The script imports schools for:
- New York City
- Los Angeles
- Chicago
- Houston
- Phoenix
- Philadelphia
- San Antonio
- San Diego
- Dallas
- San Jose
- **Charlotte** (your area!)
- Seattle
- Denver
- Boston
- Atlanta
- Miami
- Detroit
- Minneapolis
- Portland
- Las Vegas

## Adding More Metros

Edit `scripts/bulk_import_schools.py` and add more entries to the `MAJOR_METROS` list:

```python
MAJOR_METROS = [
    # ... existing metros ...
    ("Your City", north_lat, south_lat, east_lng, west_lng),
]
```

## Cost Estimate

- **Per Metro**: ~$0.40 (50 schools × $0.02 per school)
- **20 Metros**: ~$8 total
- **After Import**: Free lookups forever!

## Next Steps

1. Run the bulk import script
2. Wait for it to complete (1-2 hours)
3. Test searching for addresses - should be instant!

The route has been updated to do fast database lookups instead of calling Apify on every request.
