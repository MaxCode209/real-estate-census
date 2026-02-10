# Why Some Schools Show "N/A" - Missing Data Source Explained

## The Problem

When you look up an address, you sometimes see:
- ✅ Elementary School: **8.5** (found)
- ✅ Middle School: **7.2** (found)
- ❌ High School: **N/A** (missing)

## What's Happening

The system works in **two steps**:

### Step 1: Find Zoned Schools ✅ (This Works)
The system correctly identifies which schools are zoned for the address using:
- **Attendance zones** (point-in-polygon testing) - for NC/SC
- **Apify/GreatSchools** (web scraping) - for other states

**Result:** School names are found correctly (e.g., "West Charlotte High School")

### Step 2: Look Up Ratings ❌ (This is Where N/A Comes From)
The system then tries to match those school names to your `school_data` table to get the rating.

**The Problem:** The school name exists in zones, but **the rating doesn't exist in your `school_data` table**.

## The Missing Data Source

**Missing Data:** School ratings in the `school_data` database table

**Current Status:**
- ✅ **6,108 attendance zones** imported (school names and boundaries)
- ✅ **2,227 schools** with ratings in `school_data` table
- ❌ **Many schools from zones don't have ratings** in the database

**Why This Happens:**
1. Attendance zones were imported from NCES (National Center for Education Statistics)
2. These zones have school **names** but not **ratings**
3. School ratings come from a separate data source (GreatSchools via Apify)
4. Not all schools that have zones have been imported with ratings yet

## Example Flow

```
Address: "123 Main St, Charlotte, NC"
  ↓
Step 1: Find zoned schools (from attendance_zones table)
  → Elementary: "Smith Elementary School" ✅
  → Middle: "Smith Middle School" ✅
  → High: "West Charlotte High School" ✅
  ↓
Step 2: Look up ratings (from school_data table)
  → "Smith Elementary School" → Found rating: 8.5 ✅
  → "Smith Middle School" → Found rating: 7.2 ✅
  → "West Charlotte High School" → NOT FOUND → N/A ❌
```

## How to Fix It

### Option 1: Import Missing Schools (Recommended)

Run the script to import schools that are in zones but missing ratings:

```bash
python scripts/import_missing_schools.py
```

**What it does:**
- Finds schools in `attendance_zones` that don't have ratings in `school_data`
- Uses Apify to fetch ratings from GreatSchools
- Adds them to your `school_data` table

**Note:** This uses Apify credits (costs money), but it's the most accurate way to get ratings.

### Option 2: Bulk Import for Specific Areas

If you want to import schools for specific metro areas:

```bash
python scripts/bulk_import_schools.py --state NC
python scripts/bulk_import_schools.py --state SC
```

### Option 3: Check What's Missing

To see which schools are missing ratings:

```bash
# Check debug log
cat debug_schools.log

# Or check database directly
# Look for schools in attendance_zones that aren't in school_data
```

## Why Not All Schools Have Ratings

1. **GreatSchools doesn't rate all schools** - Some schools may not have ratings available
2. **Name mismatches** - School names in zones might not match exactly with GreatSchools
3. **Not imported yet** - You may not have imported all schools for your coverage area

## Current Coverage

Based on your setup:
- **6,108 attendance zones** (school boundaries)
- **2,227 schools with ratings** (in database)
- **~3,881 schools missing ratings** (zones exist but no ratings)

## Next Steps

1. **Check which schools are missing:**
   - Look at `debug_schools.log` after searching an address
   - It will show which school names were found but couldn't be matched

2. **Import missing schools:**
   ```bash
   python scripts/import_missing_schools.py
   ```

3. **For specific areas:**
   ```bash
   python scripts/bulk_import_schools.py --metro "Charlotte, NC"
   ```

## Summary

**The N/A appears because:**
- ✅ School name is found (from attendance zones)
- ❌ School rating is NOT in your `school_data` table

**The fix:**
- Import missing schools using `import_missing_schools.py`
- This will fetch ratings from GreatSchools and add them to your database
