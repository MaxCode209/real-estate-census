# How to Search for School Names in Supabase Database

## Quick Access

**Supabase Dashboard:** https://supabase.com/dashboard

---

## Method 1: Using Table Editor (GUI - Easiest)

### For `school_data` Table:

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click **"Table Editor"** in the left sidebar
4. Click on **`school_data`** table
5. Use the **filter/search bar** at the top:
   - Click the filter icon (funnel)
   - Select column: `elementary_school_name`, `middle_school_name`, or `high_school_name`
   - Choose operator: `is equal to` or `contains`
   - Enter school name: e.g., "Sedgefield"
   - Click "Apply"

**Example Filters:**
- `elementary_school_name` **contains** "Sedgefield"
- `middle_school_name` **is equal to** "Alexander Graham Middle"
- `high_school_name` **contains** "Myers Park"

### For `attendance_zones` Table:

1. Same steps as above
2. Click on **`attendance_zones`** table
3. Filter by `school_name` column

---

## Method 2: Using SQL Editor (More Powerful)

### Search in `school_data` Table:

1. Go to: https://supabase.com/dashboard
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New query"**
4. Paste one of these queries:

#### Find Exact School Name:
```sql
-- Search elementary schools
SELECT * 
FROM school_data 
WHERE elementary_school_name = 'Sedgefield Elementary'
LIMIT 100;
```

#### Find Schools Containing Text:
```sql
-- Search for schools containing "Sedgefield"
SELECT 
    id,
    zip_code,
    address,
    elementary_school_name,
    elementary_school_rating,
    middle_school_name,
    middle_school_rating,
    high_school_name,
    high_school_rating
FROM school_data 
WHERE elementary_school_name ILIKE '%Sedgefield%'
   OR middle_school_name ILIKE '%Sedgefield%'
   OR high_school_name ILIKE '%Sedgefield%'
LIMIT 100;
```

#### Case-Insensitive Search:
```sql
-- Case-insensitive search (finds "Sedgefield", "sedgefield", "SEDGEFIELD")
SELECT * 
FROM school_data 
WHERE LOWER(elementary_school_name) LIKE LOWER('%sedgefield%')
LIMIT 100;
```

#### Search All School Types at Once:
```sql
-- Find school in any field (elementary, middle, or high)
SELECT 
    id,
    zip_code,
    address,
    elementary_school_name,
    elementary_school_rating,
    middle_school_name,
    middle_school_rating,
    high_school_name,
    high_school_rating,
    latitude,
    longitude
FROM school_data 
WHERE elementary_school_name ILIKE '%Sedgefield%'
   OR middle_school_name ILIKE '%Sedgefield%'
   OR high_school_name ILIKE '%Sedgefield%'
ORDER BY elementary_school_name, middle_school_name, high_school_name
LIMIT 100;
```

#### Count Schools by Name:
```sql
-- Count how many records have a specific school
SELECT 
    elementary_school_name,
    COUNT(*) as count
FROM school_data 
WHERE elementary_school_name IS NOT NULL
GROUP BY elementary_school_name
HAVING elementary_school_name ILIKE '%Sedgefield%'
ORDER BY count DESC;
```

### Search in `attendance_zones` Table:

```sql
-- Find attendance zones for a school
SELECT 
    id,
    school_name,
    school_level,
    school_district,
    state,
    data_year
FROM attendance_zones 
WHERE school_name ILIKE '%Sedgefield%'
ORDER BY school_level, school_name;
```

---

## Method 3: Advanced Search Queries

### Find Schools with Ratings:
```sql
-- Find schools with ratings (not NULL)
SELECT 
    elementary_school_name,
    elementary_school_rating,
    middle_school_name,
    middle_school_rating,
    high_school_name,
    high_school_rating
FROM school_data 
WHERE (elementary_school_name ILIKE '%Sedgefield%' AND elementary_school_rating IS NOT NULL)
   OR (middle_school_name ILIKE '%Sedgefield%' AND middle_school_rating IS NOT NULL)
   OR (high_school_name ILIKE '%Sedgefield%' AND high_school_rating IS NOT NULL)
LIMIT 100;
```

### Find Schools by Zip Code AND Name:
```sql
-- Find schools in a specific zip code
SELECT * 
FROM school_data 
WHERE zip_code = '28204'
  AND (elementary_school_name ILIKE '%Sedgefield%'
       OR middle_school_name ILIKE '%Sedgefield%'
       OR high_school_name ILIKE '%Sedgefield%')
LIMIT 100;
```

### Find Schools Near a Location:
```sql
-- Find schools near coordinates (within ~5 miles)
SELECT 
    elementary_school_name,
    elementary_school_rating,
    latitude,
    longitude,
    3959 * acos(
        cos(radians(35.2271)) * cos(radians(latitude)) * 
        cos(radians(longitude) - radians(-80.8431)) + 
        sin(radians(35.2271)) * sin(radians(latitude))
    ) as distance_miles
FROM school_data 
WHERE elementary_school_name ILIKE '%Sedgefield%'
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
ORDER BY distance_miles
LIMIT 10;
```

---

## Quick Reference

### School Name Columns:

**`school_data` table:**
- `elementary_school_name` - Elementary school name
- `middle_school_name` - Middle school name
- `high_school_name` - High school name

**`attendance_zones` table:**
- `school_name` - School name
- `school_level` - 'elementary', 'middle', or 'high'

### SQL Operators:

- `=` - Exact match (case-sensitive)
- `ILIKE` - Case-insensitive pattern matching
- `LIKE` - Case-sensitive pattern matching
- `%text%` - Contains text (wildcard)
- `text%` - Starts with text
- `%text` - Ends with text

---

## Tips

1. **Use ILIKE for flexible searches** - Finds matches regardless of case
2. **Use % wildcards** - `%Sedgefield%` finds "Sedgefield Elementary", "Sedgefield Middle", etc.
3. **Check NULL values** - Some schools may have NULL names
4. **Limit results** - Always use `LIMIT` to avoid huge result sets
5. **Save queries** - Supabase SQL Editor lets you save frequently used queries

---

## Example: Find "Sedgefield Elementary"

**Quick SQL Query:**
```sql
SELECT * 
FROM school_data 
WHERE elementary_school_name ILIKE '%Sedgefield Elementary%'
LIMIT 50;
```

**Or search all school types:**
```sql
SELECT 
    elementary_school_name,
    middle_school_name,
    high_school_name,
    elementary_school_rating,
    middle_school_rating,
    high_school_rating
FROM school_data 
WHERE 'Sedgefield' IN (
    LOWER(elementary_school_name),
    LOWER(middle_school_name),
    LOWER(high_school_name)
)
LIMIT 50;
```
