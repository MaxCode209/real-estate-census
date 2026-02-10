# SABS Data Import Status

## ✅ Setup Complete

Your SABS_1516.zip file has been successfully extracted!

**Location**: `data/nces_zones/SABS_1516/`
**Shapefile**: `SABS_1516.shp` (with all companion files)

---

## 🔄 Import Process

The import script (`scripts/import_nces_zones.py`) is designed to:

1. **Read the shapefile** - This is a large file (hundreds of MB) with thousands of school attendance zones
2. **Convert to GeoJSON** - Transform the shapefile format to GeoJSON
3. **Filter for NC and SC** - Only import zones for North Carolina (FIPS 37) and South Carolina (FIPS 45)
4. **Import to database** - Insert each zone into your Supabase `attendance_zones` table

### Expected Processing Time
- **Small dataset**: 5-10 minutes
- **Full dataset**: 15-30 minutes (depending on your internet connection to Supabase)

---

## 🚀 Running the Import

If the import hasn't started or you need to run it again:

```bash
cd "c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"
python scripts/import_nces_zones.py
```

### What to Expect

The script will:
1. Find the shapefile automatically
2. Check if GeoJSON already exists (if so, skip conversion)
3. Convert shapefile → GeoJSON (if needed)
4. Filter for NC/SC zones
5. Import zones in batches of 100
6. Show progress every 100 zones
7. Display final statistics

### Sample Output
```
NCES School Attendance Zone Import
============================================================
Found shapefile: data/nces_zones/SABS_1516/SABS_1516.shp

Converting shapefile to GeoJSON...
Found 15,234 zones for NC and SC

Importing zones into database...
  Processing 100/15234...
  Processing 200/15234...
  ...
Import Complete!
  Imported: 15,234 zones
  Matched to schools: 2,456
  Skipped: 0
```

---

## 📊 After Import

Once the import completes, you can:

### 1. Export the Dataset
```bash
python scripts/export_attendance_zones.py
```

This creates:
- `data/attendance_zones_export_[timestamp].csv` - Summary
- `data/attendance_zones_export_[timestamp].json` - Full data with GeoJSON

### 2. View in Supabase
1. Go to: https://supabase.com/dashboard
2. Table Editor → `attendance_zones` table
3. See all imported zones

### 3. Test in Your App
1. Open: http://localhost:5000
2. Enter an address in NC or SC
3. The system will now use **true zoning** (point-in-polygon) instead of distance-based lookup!

---

## 🔍 Verify Import Status

### Check Database
```sql
-- In Supabase SQL Editor
SELECT 
  state, 
  school_level, 
  COUNT(*) as zone_count 
FROM attendance_zones 
GROUP BY state, school_level
ORDER BY state, school_level;
```

### Check Files
- Shapefile: `data/nces_zones/SABS_1516/SABS_1516.shp`
- GeoJSON (if converted): `data/nces_zones/zones_nc_sc.geojson`

---

## ⚠️ Troubleshooting

### If Import Fails

1. **Check geopandas is installed**:
   ```bash
   python -c "import geopandas; print('OK')"
   ```

2. **Check database connection**:
   ```bash
   python scripts/test_db_connection.py
   ```

3. **Check shapefile exists**:
   ```bash
   dir data\nces_zones\SABS_1516\*.shp
   ```

### Common Issues

- **Memory error**: The shapefile is very large. Try importing in smaller batches (modify the script)
- **Database timeout**: Supabase free tier has connection limits. The script commits in batches to avoid this
- **Missing zones**: Some zones might not import if GeoJSON is invalid

---

## 📝 Next Steps

1. ✅ **SABS data extracted** - DONE
2. ⏳ **Import zones** - IN PROGRESS (or run manually)
3. ⏸️ **Export dataset** - After import completes
4. ⏸️ **Test address search** - Verify zoning works
5. ⏸️ **Refine zones** - Add missing zones if needed

---

## 🔗 Quick Links

- **Local Map**: http://localhost:5000
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Import Script**: `scripts/import_nces_zones.py`
- **Export Script**: `scripts/export_attendance_zones.py`
