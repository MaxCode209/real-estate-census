# Google Maps API Usage & Costs

## Current Google Maps API Usage in Your Application

### APIs Currently Enabled/Used:

1. **Maps JavaScript API** ✅ (Required)
2. **Geocoding API** ✅ (Used for address/zip lookups)
3. **Places API** ✅ (Loaded but may not be actively used)
4. **Visualization API** ✅ (Used for heatmaps)
5. **Drawing API** ✅ (Loaded but may not be actively used)
6. **Geometry API** ✅ (Used for distance calculations)

---

## Where Google Maps API is Used

### Frontend (Browser - `frontend/static/js/map.js`):

1. **Map Display** (Maps JavaScript API)
   - Initial map load: `new google.maps.Map()`
   - Map interactions (zoom, pan, etc.)
   - **Cost:** Free for map loads (up to 28,000/month)

2. **Geocoding** (Geocoding API)
   - Address search: `geocoder.geocode()` 
   - Zip code geocoding: `geocodeZipCode()`
   - **Cost:** $5.00 per 1,000 requests after free tier

3. **Polygons & Boundaries** (Maps JavaScript API)
   - Zip code boundary polygons: `new google.maps.Polygon()`
   - Drawing boundaries on map
   - **Cost:** Free (part of map display)

4. **Heatmaps** (Visualization API)
   - Census data heatmap: `new google.maps.visualization.HeatmapLayer()`
   - **Cost:** Free (part of Maps JavaScript API)

5. **Markers & Info Windows** (Maps JavaScript API)
   - Location markers: `new google.maps.Marker()`
   - Info windows: `new google.maps.InfoWindow()`
   - **Cost:** Free (part of map display)

6. **Geometry Calculations** (Geometry API)
   - Distance calculations
   - **Cost:** Free (part of Maps JavaScript API)

### Backend (`backend/routes.py`):

1. **Geocoding API** (Server-side)
   - `/api/geocode-zip/<zip_code>` - Geocodes zip codes
   - `/api/schools/address` - Geocodes addresses for school lookup
   - `/api/export/report` - Geocodes addresses for report generation
   - **Cost:** $5.00 per 1,000 requests after free tier

---

## Google Maps API Pricing (2024)

### Free Tier (Monthly Credits):
- **$200 free credit per month** (applied automatically)
- Credits cover most light-to-moderate usage

### Cost After Free Tier:

| API Service | Cost per 1,000 Requests | Free Tier |
|-------------|------------------------|-----------|
| **Maps JavaScript API** | $7.00 | First 28,000 loads/month |
| **Geocoding API** | $5.00 | First 40,000 requests/month |
| **Places API** | Varies by call type | First 1,000 requests/month |
| **Visualization API** | Free | Included with Maps JS API |
| **Geometry API** | Free | Included with Maps JS API |

### Your Estimated Monthly Usage:

**Maps JavaScript API:**
- Map loads: ~100-500/month (depending on usage)
- **Cost:** $0 (well within free tier)

**Geocoding API:**
- Address searches: ~50-200/month
- Zip code geocoding: ~50-200/month
- **Cost:** $0 (well within free tier)

**Total Estimated Monthly Cost:** **$0** (within free tier)

---

## What Triggers API Calls

### Maps JavaScript API Calls:
1. ✅ **Page load** - Every time someone opens the map (1 call)
2. ✅ **Map interactions** - Panning, zooming (free, no API call)
3. ✅ **Polygon rendering** - Drawing zip boundaries (free, no API call)
4. ✅ **Heatmap rendering** - Displaying census data (free, no API call)

### Geocoding API Calls:
1. ✅ **Search by Address** - When user searches an address
2. ✅ **Search by Zip Code** - When user searches a zip code
3. ✅ **Export Report** - When generating Word/PDF report (if address needs geocoding)
4. ✅ **School Lookup** - When looking up schools for an address

---

## Cost Optimization Tips

### Current Usage is Very Efficient:
- ✅ Map loads are cached (browser cache)
- ✅ Geocoding results could be cached (not currently implemented)
- ✅ Most map interactions are free (no API calls)

### Potential Optimizations:

1. **Cache Geocoding Results** (Recommended)
   - Store geocoded addresses/zip codes in database
   - Reduces API calls for repeat searches
   - **Savings:** Could reduce Geocoding API calls by 50-80%

2. **Use Zip Code Database** (Optional)
   - Pre-populate zip code centroids in database
   - Only geocode addresses, not zip codes
   - **Savings:** Reduces Geocoding API calls for zip searches

3. **Batch Geocoding** (For bulk operations)
   - If doing bulk imports, use batch geocoding
   - More efficient than individual calls

---

## Monitoring Your Usage

### Check Your Current Usage:
1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: **APIs & Services** → **Dashboard**
4. Click on **Maps JavaScript API** or **Geocoding API**
5. View **Quotas** tab to see current usage

### Set Up Billing Alerts:
1. Go to: **Billing** → **Budgets & alerts**
2. Create a budget alert (e.g., $10/month)
3. Get notified if usage exceeds free tier

---

## Summary

### Current Cost: **$0/month** ✅
- Your usage is well within Google's free tier
- $200/month credit covers typical usage
- No billing setup required for current usage level

### APIs You're Using:
1. **Maps JavaScript API** - Map display, polygons, markers (FREE)
2. **Geocoding API** - Address/zip code lookups ($5/1K after free tier)
3. **Visualization API** - Heatmaps (FREE)
4. **Geometry API** - Distance calculations (FREE)

### Estimated Monthly Calls:
- **Maps JavaScript API:** ~100-500 loads (FREE)
- **Geocoding API:** ~100-400 requests (FREE)

### When You'd Start Paying:
- If you exceed **40,000 Geocoding requests/month** → ~$0.005 per request
- If you exceed **28,000 map loads/month** → ~$0.007 per load
- **Very unlikely** for single-user or small team usage

---

## Recommendation

**You're in good shape!** Your current usage is well within the free tier. No action needed unless:
- You start doing bulk imports (100+ addresses/day)
- You have multiple users accessing the app simultaneously
- You want to add caching to reduce API calls further

**Next Steps (Optional):**
- Set up billing alerts to monitor usage
- Consider caching geocoding results for repeat searches
- Monitor usage monthly to track trends
