# All Data Sources & Links Used in This Project

## 📊 Census & Demographic Data

### 1. US Census Bureau API
**Purpose:** Population, income, age demographics by zip code  
**URL:** https://api.census.gov/data/  
**API Key Signup:** https://api.census.gov/data/key_signup.html  
**Cost:** FREE  
**Rate Limits:**
- Without API key: 500 requests/day
- With API key: 5,000 requests/day

**What We Use:**
- Population data
- Average household income (AHHI)
- Median age
- Zip Code Tabulation Areas (ZCTA)

**Documentation:**
- API Explorer: https://api.census.gov/data.html
- Variables List: https://api.census.gov/data/2023/acs/acs5/variables.html

---

### 2. Census TIGER/Line Files
**Purpose:** Official zip code boundary polygons (ZCTA)  
**URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html  
**Cost:** FREE  
**Format:** Shapefiles (converted to GeoJSON)

**TIGERweb REST API:**
- Current: https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/2/query
- ACS 2022: https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2022/MapServer/2/query
- ACS 2021: https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2021/MapServer/2/query

**What We Use:**
- ZCTA (Zip Code Tabulation Area) boundaries
- Accurate zip code polygon shapes

---

## 🏫 School Data

### 3. NCES (National Center for Education Statistics)
**Purpose:** School attendance zone boundaries  
**URL:** https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries  
**Cost:** FREE  
**Format:** Shapefiles (SABS - School Attendance Boundary Survey)

**What We Use:**
- School attendance zone polygons
- School names and levels (elementary, middle, high)
- School districts
- State coverage: NC, SC (and others)

**Data Year:** 2015-2016 (SABS_1516)

---

### 4. GreatSchools.org
**Purpose:** School ratings and information  
**URL:** https://www.greatschools.org  
**Cost:** FREE (via web scraping)  
**Access Method:** Via Apify actor

**What We Use:**
- School ratings (1-10 scale)
- School names and addresses
- Zoned schools for addresses

**Note:** Accessed through Apify, not directly

---

### 5. Apify Platform
**Purpose:** Web scraping service for GreatSchools/Zillow school data  
**URL:** https://apify.com  
**API Base:** https://api.apify.com/v2  
**Cost:** Pay-per-use (credits)  
**Actor Used:** `axlymxp~zillow-school-scraper`

**What We Use:**
- Scrapes school data from GreatSchools and Zillow
- Gets zoned schools for addresses
- Fetches school ratings

**Account Required:** Yes (with API token)

---

## 🗺️ Geocoding & Maps

### 6. Google Maps API
**Purpose:** Address geocoding, map display, reverse geocoding  
**URL:** https://console.cloud.google.com/  
**APIs Used:**
- Maps JavaScript API
- Geocoding API

**Cost:** 
- Free tier: $200/month credit
- Then pay-per-use

**What We Use:**
- Geocode addresses to lat/lng
- Display interactive maps
- Get zip codes from addresses
- Get approximate boundaries (fallback)

**Documentation:**
- Maps JavaScript API: https://developers.google.com/maps/documentation/javascript
- Geocoding API: https://developers.google.com/maps/documentation/geocoding

---

## 📍 Zip Code Boundaries (Alternative Sources)

### 7. OpenDataSoft API
**Purpose:** Public zip code boundaries  
**URL:** https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/us-zip-code-labels-and-boundaries/records  
**Cost:** FREE  
**Format:** GeoJSON

**What We Use:**
- Primary source for zip code boundaries
- Fallback when local files don't exist

---

### 8. GitHub - OpenDataDE
**Purpose:** Pre-processed zip code GeoJSON files  
**URL:** https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master  
**Cost:** FREE  
**Format:** GeoJSON

**URL Patterns:**
- By first digit: `/{zip_code[0]}/{zip_code}_polygon.geojson`
- ZCTA5 format: `/zcta5/{zip_code}_polygon.geojson`

**What We Use:**
- Fallback source for zip boundaries
- State-organized GeoJSON files

---

### 9. Boundaries.io (Optional)
**Purpose:** Commercial zip code boundary service  
**URL:** https://boundaries.io  
**API:** https://boundaries.io/api/v1/boundary  
**Free Alternative:** https://boundaries-io.herokuapp.com/zip/{zip_code}  
**Cost:** Free tier available, then paid

**What We Use:**
- Alternative boundary source (if API key configured)
- Fallback option

---

## 💾 Database & Storage

### 10. Supabase (PostgreSQL)
**Purpose:** Cloud PostgreSQL database  
**URL:** https://supabase.com/dashboard  
**Cost:** FREE tier available (500MB database)  
**Host:** `aws-0-us-west-2.pooler.supabase.com`

**What We Store:**
- `census_data` table - Census demographics
- `school_data` table - School ratings
- `attendance_zones` table - School zone boundaries

**Dashboard:** https://supabase.com/dashboard

---

## 📁 Local Storage

### 11. Local File System
**Purpose:** Store downloaded boundaries and data  
**Directories:**
- `data/zip_boundaries/` - GeoJSON boundary files
- `data/nces_zones/` - NCES attendance zone shapefiles
- `data/` - Other exported data files

**What We Store:**
- Downloaded zip code boundaries (GeoJSON)
- NCES attendance zone data
- Exported CSV/JSON files

---

## 🔗 Quick Reference Links

### Primary Data Sources
1. **Census API:** https://api.census.gov/data/
2. **Census TIGERweb:** https://tigerweb.geo.census.gov/
3. **NCES Boundaries:** https://nces.ed.gov/programs/edge/Geographic/SchoolAttendanceBoundaries
4. **GreatSchools:** https://www.greatschools.org
5. **Apify:** https://apify.com
6. **Google Maps:** https://console.cloud.google.com/
7. **Supabase:** https://supabase.com/dashboard

### Boundary Sources (in priority order)
1. **Local files:** `data/zip_boundaries/{zip_code}.geojson`
2. **Census TIGERweb:** https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/2/query
3. **OpenDataSoft:** https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/us-zip-code-labels-and-boundaries/records
4. **GitHub CDN:** https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master
5. **Boundaries.io:** https://boundaries.io/api/v1/boundary (if API key set)
6. **Google Geocoding:** Approximate boundaries (fallback)

### School Data Sources (in priority order)
1. **Attendance Zones (NCES):** Point-in-polygon testing
2. **Apify/GreatSchools:** Web scraping for zoned schools
3. **Distance-based lookup:** Nearest schools in database

---

## 💰 Cost Summary

| Source | Cost | Notes |
|--------|------|-------|
| Census Bureau API | **FREE** | Optional API key for higher limits |
| Census TIGERweb | **FREE** | Official government data |
| NCES Boundaries | **FREE** | Public education data |
| Google Maps API | **Free tier** | $200/month credit, then pay-per-use |
| Apify | **Pay-per-use** | Credits required for scraping |
| GreatSchools | **FREE** | Via Apify scraping |
| OpenDataSoft | **FREE** | Public API |
| GitHub CDN | **FREE** | Open source |
| Supabase | **Free tier** | 500MB database free |
| Boundaries.io | **Free tier** | Optional, has paid plans |

---

## 📝 API Keys & Credentials Needed

### Required
- ✅ **Google Maps API Key** - For geocoding and maps
- ✅ **Supabase/Database URL** - For data storage

### Optional (but recommended)
- ⚠️ **Census API Key** - For higher rate limits (FREE)
- ⚠️ **Apify API Token** - For school data scraping (PAID)
- ⚠️ **Boundaries.io API Key** - Alternative boundary source (FREE tier available)

---

## 🔄 Data Flow

```
Address Search
  ↓
Google Maps Geocoding API → Get lat/lng
  ↓
Census TIGERweb / Local Files → Get zip boundary
  ↓
NCES Attendance Zones → Find zoned schools
  ↓
Apify/GreatSchools → Get school ratings
  ↓
Census Bureau API → Get demographics
  ↓
Supabase Database → Store/Retrieve all data
```

---

## 📚 Documentation Links

- **Census API Docs:** https://www.census.gov/data/developers/data-sets.html
- **TIGER/Line Files:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- **NCES Documentation:** https://nces.ed.gov/programs/edge/
- **Google Maps Docs:** https://developers.google.com/maps/documentation
- **Apify Docs:** https://docs.apify.com/
- **Supabase Docs:** https://supabase.com/docs

---

## 🎯 Current Data Coverage

- **Census Data:** 13,668 zip codes in database
- **School Zones:** 6,108 attendance zones (NC/SC)
- **School Ratings:** 2,230 schools with ratings
- **Zip Boundaries:** 2,252 boundary files (and growing)

---

*Last Updated: Based on current project state*
