# Quick Start - Application Links & Dataset Export

## 🚀 Application Running

Your Flask application is now running locally!

### Local Map Application
**URL**: http://localhost:5000

This is your locally hosted map where you can:
- Search by zip code or address
- View census data overlays
- Get school ratings for addresses
- Export data to CSV

### See school zoning debug output in the terminal

The `[ZONED SCHOOLS]` print statements only appear in the **same terminal where the Flask server is running**, and **only when you look up an address** in the UI (which calls `/api/schools/address`).

1. **Start the backend** from the project root (this terminal will show the prints):
   ```bash
   cd "c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"
   python -u app.py
   ```
   The app runs with `use_reloader=False` so the same process handles requests and `[ZONED SCHOOLS]` prints appear in this terminal. (With the reloader on, a child process handles requests and its prints often don’t show.)

2. In your browser, open **http://localhost:5000** and **search for an address** (e.g. type an address and run the search / address lookup that shows school scores).

3. Watch the **same terminal** where you ran `python -u app.py`. You should see a block like:
   ```
   ============================================================
   [ZONED SCHOOLS] ADDRESS LOOKUP REQUEST
   ============================================================
     Address: '123 Main St, Charlotte, NC 28204'
     Coords:  lat=35.xxx, lng=-80.xxx
   ------------------------------------------------------------
   [ZONED SCHOOLS] Step 1: Calling Apify ...
   ...
   [ZONED SCHOOLS] >>> DRIVING THE UI: SOURCE=apify
   ```

If you run the app some other way (e.g. another IDE "Run" button), use the terminal/console that is attached to that process to see the prints.

**Check that the backend is really receiving the request**

1. Start the app in **Terminal 1**: `python -u app.py` (leave it running).
2. Open **Terminal 2** and run this (one line):
   ```bash
   curl "http://localhost:5000/api/schools/address?address=123%20Main%20St,%20Charlotte,%20NC%2028204&lat=35.2&lng=-80.8"
   ```
3. Look at **Terminal 1**. You should see `[ZONED SCHOOLS] >>> /api/schools/address was called <<<` and the rest of the block.
4. If nothing appears in Terminal 1, the request is not reaching your Flask server (e.g. wrong port or another process is serving the page).

---

## 🗄️ Database Access (Supabase)

### Supabase Dashboard
**URL**: https://supabase.com/dashboard

### Direct Database Connection
- **Host**: `aws-0-us-west-2.pooler.supabase.com`
- **Database**: `postgres`
- **Connection String**: (stored in `.env` file)

### View Your Data
1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click **"Table Editor"** in the left sidebar
4. View tables:
   - `census_data` - Census demographics by zip code
   - `school_data` - School ratings by address/zip
   - `attendance_zones` - School attendance zone boundaries (GeoJSON)

### SQL Editor
1. In Supabase dashboard → **SQL Editor**
2. Run queries like:
```sql
-- View all attendance zones
SELECT school_name, school_level, state, school_district 
FROM attendance_zones 
ORDER BY state, school_level;

-- Count zones by state
SELECT state, COUNT(*) as zone_count 
FROM attendance_zones 
GROUP BY state;
```

---

## 📊 Export Attendance Zones Dataset

### Current Status
The export script found **0 attendance zones** in your database. This means you need to import attendance zone data first.

### To Export Attendance Zones (once data exists):
```bash
python scripts/export_attendance_zones.py
```

This will create:
- `data/attendance_zones_export_[timestamp].csv` - Summary without GeoJSON
- `data/attendance_zones_export_[timestamp].json` - Full data with GeoJSON boundaries

### To Import Attendance Zones:

#### Option 1: Import from NCES (National Center for Education Statistics)
```bash
python scripts/import_nces_zones.py
```

#### Option 2: Manual Import
1. Download school attendance zone boundaries from:
   - NCES: https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries
   - Or your local school district websites
2. Convert to GeoJSON format
3. Import using the database import script

---

## 🎯 Refining Zoned Schools Selection

### Current Implementation
The system uses **point-in-polygon** testing to find zoned schools:
1. User enters an address
2. Address is geocoded to lat/lng
3. System checks which attendance zone polygons contain that point
4. Returns the zoned school for that address

### To Improve Accuracy:
1. **Export current zones**: Use the export script to see what zones you have
2. **Identify gaps**: Compare with actual school district boundaries
3. **Add missing zones**: Import additional zone data
4. **Validate boundaries**: Check that GeoJSON polygons are accurate

### Testing Zoned Schools
1. Open http://localhost:5000
2. Enter an address in the "Search Address" field
3. The system will:
   - Geocode the address
   - Check attendance zones (if available)
   - Fall back to distance-based lookup if no zones found
   - Display school ratings

---

## 📁 Data Files Location

- **Census Data**: Stored in Supabase `census_data` table
- **School Data**: Stored in Supabase `school_data` table  
- **Attendance Zones**: Stored in Supabase `attendance_zones` table
- **Exported Files**: `data/` directory
- **Zip Boundaries**: `data/zip_boundaries/` directory (GeoJSON files)

---

## ✅ Current Status

### Zoned Schools Implementation
- ✅ **6,108 attendance zones** imported with correct school names
- ✅ **Coordinate transformation** fixed (Web Mercator → WGS84)
- ✅ **Point-in-polygon testing** working correctly
- ✅ **School name matching** improved (handles "PreK-8" vs "Elementary")
- ⚠️ **2,227 schools in database** - Many schools from zones are missing ratings

### What's Working
1. ✅ Zoned schools are found correctly using point-in-polygon
2. ✅ School names match to database (with fuzzy matching)
3. ✅ System uses zoned schools approach (not distance-based)

### What Needs Work
1. ⚠️ **Missing schools**: Many schools from zones aren't in `school_data` table
2. ⚠️ **Need to import more schools**: Run `python scripts/import_missing_schools.py` to add schools

---

## 🔧 Next Steps

1. **Bulk Import Census Data** (RECOMMENDED): Run `python scripts/bulk_import_all_census_data.py` to download ALL census data (~33,000 zip codes). This is a one-time operation that takes 5-15 minutes. Once complete, you won't need to call the Census API on-demand.
2. **Import More Schools**: Run `python scripts/import_missing_schools.py` to add missing schools
3. **Test Address Search**: Try "1010 kenliworth ave charlotte nc" - should show zoned schools
4. **Check Debug Log**: Look for `debug_schools.log` file for detailed logs
5. **Export Dataset**: Use export script to review coverage

---

## 📝 Quick Commands

```bash
# Start the application
python app.py

# Bulk import ALL census data (one-time, ~5-15 minutes)
python scripts/bulk_import_all_census_data.py

# Export attendance zones
python scripts/export_attendance_zones.py

# Import NCES zones
python scripts/import_nces_zones.py

# Test school districts (zip) pipeline (NC/SC) — e.g. zip 28202
python scripts/test_school_zones_api.py 28202

# Check database connection
python scripts/test_db_connection.py
```

---

## 🔗 Important Links Summary

- **Local Map**: http://localhost:5000
- **Supabase Dashboard**: https://supabase.com/dashboard
- **NCES School Boundaries**: https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries
- **Census TIGER Boundaries**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
