# How to Monitor the School Data Import

## Quick Status Check

Run this command anytime to see the current import status:

```bash
python scripts/check_import_status.py
```

This will show you:
- ✅ Total schools imported
- ✅ Progress percentage
- ✅ Estimated cost so far
- ✅ Recent schools added
- ✅ Completion status

## Current Status

**Last Check:** 397 schools imported (9.9% complete)
**Cost So Far:** ~$7.94
**Expected Total:** ~4,000 schools
**Expected Total Cost:** ~$80

## Monitor in Real-Time

### Option 1: Watch the Terminal Output
If the import script is still running in a terminal, you'll see:
- Progress for each region (1/11, 2/11, etc.)
- Schools added per region
- Running cost total
- Final summary when complete

### Option 2: Check Database Directly (Supabase)
1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click **"Table Editor"** → **`school_data`** table
4. See all imported schools in real-time
5. Check the count at the bottom of the table

### Option 3: Run Status Script Periodically
```bash
# Run every 30 seconds
python scripts/check_import_status.py
```

## What to Expect

### Timeline
- **Per Region:** 30-60 seconds
- **11 Regions Total:** ~10-15 minutes of Apify scraping
- **Plus Processing:** ~20-30 minutes total

### Progress Indicators
- **0-500 schools:** Early stages (Regions 1-3)
- **500-1,500 schools:** Mid-way (Regions 4-7)
- **1,500-3,000 schools:** Almost done (Regions 8-10)
- **3,000-4,000 schools:** Final regions (Region 11)

### When It's Complete
The script will print:
```
============================================================
Import complete!
Total schools imported: [number]
Total cost: $[amount]
============================================================
```

## Check Import Completion

### Method 1: Status Script
```bash
python scripts/check_import_status.py
```
Look for: `[COMPLETE] Import appears to be COMPLETE!`

### Method 2: Database Count
In Supabase SQL Editor, run:
```sql
SELECT COUNT(*) as total_schools FROM school_data;
```
Should show ~3,500-4,500 schools when complete.

### Method 3: Check Terminal
If the script is still running, wait for the final summary message.

## Troubleshooting

### Import Stopped Early
- Check if there were any errors in the terminal
- Verify Apify API token is still valid
- Check Apify account balance
- Re-run the script - it will skip already imported schools

### Low School Count
- Each region returns up to 50 schools per query
- This is normal - Apify may have limits per query
- The script processes all 11 regions to get full coverage
- Some overlap is expected and handled by deduplication

## After Import Completes

Once you see ~3,500-4,500 schools imported:
1. ✅ All addresses in NC/SC will have instant school lookups
2. ✅ No more 30-60 second waits for API calls
3. ✅ School scores display immediately on the map
4. ✅ Data is stored permanently in your database

## Quick Commands Reference

```bash
# Check status
python scripts/check_import_status.py

# View in Supabase
# Go to: https://supabase.com/dashboard → Table Editor → school_data

# Re-run import (if needed)
python scripts/bulk_import_schools.py --yes
```
