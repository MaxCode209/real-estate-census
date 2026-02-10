# True School Zoning - Setup Instructions

## ✅ What's Already Done

1. ✅ **Database table created** - `attendance_zones` table is ready
2. ✅ **Code implemented** - Zone-based lookup logic is in place
3. ✅ **Shapely installed** - Geometry library ready
4. ✅ **Geopandas installed** - For shapefile conversion

## ⏳ What You Need To Do

### Step 1: Install Fiona (if needed)
The shapefile conversion requires `fiona`. Try installing it:
```bash
pip install fiona
```

If that fails due to permissions, you may need to:
- Run as administrator, OR
- Use `pip install --user fiona`

### Step 2: Download NCES Data

1. **Go to**: https://nces.ed.gov/programs/edge/sabs
2. **Download**: "2015-2016 School Level Shapefile" (684 MB ZIP file)
3. **Extract** the ZIP file
4. **Create directory**: `data/nces_zones/` (if it doesn't exist)
5. **Copy shapefiles** to `data/nces_zones/`:
   - The `.shp` file (main shapefile)
   - The `.dbf` file (data)
   - The `.shx` file (index)
   - Any other related files (.prj, .cpg, etc.)

### Step 3: Run Import Script

Once the shapefiles are in place:
```bash
python scripts/import_nces_zones.py
```

The script will:
1. Check for shapefiles
2. Convert to GeoJSON (filtering for NC and SC only)
3. Import zones into database
4. Match zones to schools in your database

## Expected Results

After import, you should see:
- Thousands of attendance zones imported
- Zones matched to schools in your database
- True zoning enabled for addresses in NC and SC

## Testing

After import, test by:
1. Starting your Flask app: `python app.py`
2. Searching an address in NC or SC
3. The system will use zone-based lookup if zones are available
4. Falls back to distance-based if no zones found

## Troubleshooting

### "No shapefiles found"
- Make sure shapefiles are in `data/nces_zones/`
- Check that `.shp`, `.dbf`, and `.shx` files are present

### "geopandas not installed"
- Run: `pip install geopandas fiona`

### "fiona installation failed"
- Try: `pip install --user fiona`
- Or run terminal as administrator

### Import is slow
- This is normal - processing thousands of zones takes time
- The script shows progress every 100 zones

## Current Status

- ✅ Code: Ready
- ✅ Database: Table created
- ⏳ Data: Need NCES shapefiles
- ⏳ Import: Waiting for data

Once you download the NCES data and place it in `data/nces_zones/`, just run the import script!
