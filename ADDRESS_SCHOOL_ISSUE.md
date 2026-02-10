# Why Your Address Shows Wrong Schools

## The Problem

**Address:** 1111 metropolitan ave charlotte nc 28204

**What You're Getting:**
- Elementary: **N/A** (should be Sedgefield Elementary)
- Middle: **Alexander Graham Middle (3/10)** (should be Sedgefield Middle (3/10))
- High: **Myers Park High (7/10)** ✅ (correct)

**What GreatSchools Shows:**
- Elementary: **Sedgefield Elementary**
- Middle: **Sedgefield Middle (3/10)**
- High: **Myers Park High (7/10)** ✅

## Root Cause

The **attendance zone boundaries in your database are incorrect** for this address.

### What's Happening

1. **Attendance zones find wrong schools:**
   - Your database zones say this address is zoned for:
     - **Dilworth Elementary** (not Sedgefield Elementary)
     - **Alexander Graham Middle** (not Sedgefield Middle)
     - **Myers Park High** ✅ (correct)

2. **Why Elementary shows N/A:**
   - The system finds "Dilworth Elementary" from zones
   - But "Dilworth Elementary" doesn't exist in your `school_data` table
   - So it shows N/A

3. **Why Middle shows wrong school:**
   - The system finds "Alexander Graham Middle" from zones
   - "Alexander Graham Middle" exists in your database with rating 3/10
   - So it shows that (wrong school, but correct rating)

## Why This Happens

The attendance zone data comes from **NCES (National Center for Education Statistics)**, which:
- May be **outdated** (school boundaries change over time)
- May have **inaccuracies** in the boundary polygons
- May not match current **school district assignments**

GreatSchools uses more current data, which is why it shows the correct schools.

## Solutions

### Option 1: Use Apify/GreatSchools Instead of Zones (Recommended)

Modify the code to **prioritize Apify/GreatSchools** over attendance zones when available. This will use the same data source as GreatSchools website.

**Pros:**
- More accurate, current data
- Matches what users see on GreatSchools

**Cons:**
- Slower (30-60 seconds per lookup)
- Costs Apify credits

### Option 2: Update Attendance Zones

Import newer attendance zone data or manually correct zones for areas you care about.

**Pros:**
- Fast lookups once fixed
- No ongoing costs

**Cons:**
- Time-consuming to update
- May still have inaccuracies

### Option 3: Hybrid Approach (Current, but needs fix)

Keep current approach but:
1. **Verify zones against GreatSchools** for important areas
2. **Fall back to Apify** when zones seem wrong
3. **Flag mismatches** for manual review

## Quick Fix

For now, the system is working as designed - it's using the attendance zones from NCES, which are incorrect for this address. The zones say this address is in Dilworth Elementary and Alexander Graham Middle zones, but GreatSchools (which has more current data) says it should be Sedgefield Elementary and Sedgefield Middle.

**To get correct results:**
- The system should use Apify/GreatSchools when zones fail or seem incorrect
- Or you need to update the attendance zone boundaries in your database

## Testing

I created a test script that shows:
- Location: 35.2123697, -80.83496819999999
- Zones found: Dilworth Elementary, Alexander Graham Middle, Myers Park High
- Expected: Sedgefield Elementary, Sedgefield Middle, Myers Park High

The zone boundaries in your database are placing this address in the wrong zones.
