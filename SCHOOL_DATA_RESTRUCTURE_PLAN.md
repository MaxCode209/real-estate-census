# School Data Restructure Plan

**Goal:** Once we have physical addresses for schools from NCES, restructure the schema so we can precisely suggest zoned schools when a user enters an address.

---

## Implementation Status

| Step | Status | Command |
|------|--------|---------|
| 1. Create `schools` table | Done | Migration applied |
| 2. Add `canonical_school_id` to attendance_zones | Done | Migration applied |
| 3. School model in models.py | Done | |
| 4. Populate `schools` from school_data | Ready | `python scripts/populate_schools_table.py` |
| 5. Link zones to schools | Ready | `python scripts/link_attendance_zones_to_schools.py` |
| 6. Update API to use schools | Pending | |

**Run order (after NCES populate completes):**
1. `python scripts/populate_schools_table.py`
2. `python scripts/link_attendance_zones_to_schools.py`
3. `python scripts/populate_total_schools.py` (refresh census counts)

---

## Current Flow (and its limits)

1. **User enters address** → Geocode to (lat, lng)
2. **Point-in-polygon** against `attendance_zones` → Get zones containing the point → school names
3. **Rating/address lookup** → Query `school_data` by name (fuzzy `ILIKE`), take first match

**Problems:**
- `school_data` is property-centric (one row = one property + 3 schools). Same school appears on many rows.
- Fuzzy name match can return wrong school or wrong address (property address, not school address).
- No single canonical record per school with physical location.

---

## Proposed Structure

### 1. New table: `schools` (canonical, one row per unique school)

| Column | Type | Notes |
|--------|------|-------|
| id | serial PK | |
| name | varchar(255) | School name |
| level | varchar(50) | 'elementary', 'middle', 'high' |
| address | varchar(500) | Full street address (from NCES) |
| city | varchar(100) | |
| state | varchar(2) | NC, SC |
| zip_code | varchar(10) | From NCES address |
| latitude | float | School's physical location |
| longitude | float | |
| rating | float | 1-10, best from school_data |
| nces_id | varchar(20) | NCES school ID (optional, for dedup) |
| created_at, updated_at | timestamptz | |

**Unique constraint:** (name, level) or (nces_id) when available.

**Populated from:**
- NCES: address, lat, lng, zip
- school_data: aggregate best rating across rows

### 2. Update `attendance_zones`

Add optional FK to link zone → school:

| New column | Type | Notes |
|------------|------|-------|
| school_id | int FK → schools.id | Nullable; set when we match zone to school |

**Population:** Match `attendance_zones.school_name` + `school_level` to `schools.name` + `schools.level` (fuzzy). When match found, set `school_id`.

### 3. Keep `school_data` (as raw source)

- Retain for Apify/imports and rating aggregation.
- Use to feed `schools.rating` and to backfill/validate.

---

## Improved Address Lookup Flow

```
User enters address
       ↓
Geocode → (lat, lng)
       ↓
Point-in-polygon against attendance_zones
       ↓
Get zones containing point (school_name, school_level per zone)
       ↓
For each zone:
  - If zone.school_id set → JOIN schools ON zone.school_id
  - Else → lookup schools by name+level (fuzzy fallback)
       ↓
Return: zoned schools with address, lat/lng, rating
```

**Benefits:**
- Use the school's **physical address** (from NCES), not property address
- Use the school's **actual lat/lng** for map pins and distance
- Cleaner name matching via `school_id` when linked
- Single source of truth per school

---

## Implementation Steps

### Phase 1: Create `schools` table

```sql
CREATE TABLE schools (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  level VARCHAR(50) NOT NULL,
  address VARCHAR(500),
  city VARCHAR(100),
  state VARCHAR(2),
  zip_code VARCHAR(10),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  rating DOUBLE PRECISION,
  nces_id VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ
);
CREATE INDEX idx_schools_name_level ON schools(name, level);
CREATE INDEX idx_schools_zip ON schools(zip_code);
```

### Phase 2: Populate `schools` from school_data + NCES

- Script: for each unique (name, level) in school_data:
  - If we have NCES address (elementary_school_address etc.): use it, parse zip
  - Else: call NCES API for address, lat, lng
  - Rating: MAX or AVG from school_data rows
  - INSERT into schools

### Phase 3: Link `attendance_zones` to `schools`

- Add `school_id` column to attendance_zones
- For each zone: fuzzy match (school_name, school_level) → schools
- Set zone.school_id when confident match

### Phase 4: Update API / zone utils

- `get_all_zoned_schools_for_address` (and similar): after point-in-polygon, join to `schools` via `school_id` or name+level
- Return full school details (address, rating, lat/lng) from `schools`

### Phase 5 (Optional): PostGIS for faster point-in-polygon

- Add PostGIS, store zones with `geometry(Geometry, 4326)`
- Query: `SELECT * FROM attendance_zones WHERE ST_Contains(zone_geom, ST_Point(lng, lat))`
- Replaces Python loop over all zones (faster for 6k+ zones)

---

## Zoning Logic Improvements

| Improvement | How |
|-------------|-----|
| **Precise school address** | From `schools` table (NCES) |
| **School location for map** | schools.latitude, schools.longitude |
| **Faster rating lookup** | Direct join via school_id |
| **Name disambiguation** | One canonical school per (name, level) |
| **Zone validation** | Optional: check school lat/lng falls inside its zone polygon |

---

## Summary

| Table | Role |
|-------|------|
| **schools** | Canonical list: one row per school, address + lat/lng + rating |
| **attendance_zones** | Zone polygons + school_id → schools |
| **school_data** | Raw Apify data, feeds schools.rating |

**Address → Zoned schools:** Geocode → point-in-polygon → join zones to schools → return full details.
