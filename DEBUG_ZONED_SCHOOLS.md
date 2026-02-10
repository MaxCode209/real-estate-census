# 🔍 Debugging Zoned Schools Lookup

## Issue
When testing address "1010 kenliworth ave charlotte nc", the system is not returning zoned schools - it's falling back to distance-based lookup.

## Changes Made

### 1. Added Debug Logging to `backend/routes.py`
- Logs when zones are loaded from database
- Logs when point-in-polygon test runs
- Logs which zoned schools are found (if any)
- Logs school name matching attempts
- Logs whether using zones or falling back to distance-based

### 2. Added Debug Logging to `backend/zone_utils.py`
- Logs how many zones are being tested for each school level
- Logs progress every 500 zones tested
- Logs when a match is found
- Logs errors (first 5 only to avoid spam)

## How to Debug

### Step 1: Test the Address Again
1. Open the app: http://localhost:5000
2. Enter address: "1010 kenliworth ave charlotte nc"
3. Check the **Flask console/terminal** where `app.py` is running
4. Look for `[DEBUG]` messages

### Step 2: What to Look For

**Expected Debug Output:**
```
[DEBUG] get_schools_by_address: address=1010 kenliworth ave charlotte nc, lat=35.xxx, lng=-80.xxx
[DEBUG] Loaded 6108 attendance zones from database
[DEBUG] Converted 6108 zones to dict format
[DEBUG] Testing point-in-polygon for lat=35.xxx, lng=-80.xxx
[DEBUG] find_zoned_schools: Testing 3528 elementary zones for point (35.xxx, -80.xxx)
[DEBUG] find_zoned_schools: Tested 500/3528 elementary zones...
[DEBUG] find_zoned_schools: Tested 1000/3528 elementary zones...
...
[DEBUG] find_zoned_schools: FOUND MATCH! elementary school: [School Name]
[DEBUG] Zoned schools found:
  - Elementary: [School Name]
  - Middle: [School Name] or None
  - High: [School Name] or None
[DEBUG] use_zones = True (will use zones)
[DEBUG] Looking up elementary school rating for: '[School Name]'
[DEBUG] Found rating: X.X for [School Name]
```

**If No Zones Found:**
```
[DEBUG] find_zoned_schools: No elementary zone found after testing 3528 zones
[DEBUG] No zoned schools found - falling back to distance-based lookup
```

### Step 3: Possible Issues

#### Issue 1: Zones Not Covering Address
- **Symptom**: All zones tested but none match
- **Cause**: Address might not be in any attendance zone
- **Solution**: Check if address is actually in a school zone (might be unzoned area)

#### Issue 2: Geometry Format Issue
- **Symptom**: Errors in `find_zoned_schools` like "Error checking zone..."
- **Cause**: Zone boundaries might be in wrong format
- **Solution**: Check zone format with `scripts/test_zone_format.py`

#### Issue 3: School Name Matching Failing
- **Symptom**: Zones found but "No rating found in school_data"
- **Cause**: School name from zone doesn't match name in `school_data` table
- **Solution**: Improve fuzzy matching or check name variations

#### Issue 4: Zones Not Loading
- **Symptom**: "No zones found in database!"
- **Cause**: Database query failing or zones not imported
- **Solution**: Check database connection and run `scripts/check_zones_status.py`

## Next Steps

1. **Test the address again** and check Flask console output
2. **Share the debug output** so we can identify the issue
3. **If zones are found but ratings aren't**: Check school name matching
4. **If no zones are found**: Check if address is actually in a zone

## Quick Test Commands

```bash
# Check zones status
python scripts/check_zones_status.py

# Test zone format
python scripts/test_zone_format.py

# Check Flask logs (when app is running)
# Look for [DEBUG] messages in the terminal
```

## Files Modified

- `backend/routes.py` - Added debug logging to `/schools/address` endpoint
- `backend/zone_utils.py` - Added debug logging to `find_zoned_schools()` function
