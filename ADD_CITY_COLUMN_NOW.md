# Add City Column to census_data (do this once)

If the **Supabase SQL Editor** gives "Query read timeout", use the script below instead (it uses a direct connection and a longer timeout).

---

## Option A: Run from your machine (recommended if SQL Editor times out)

From the project folder, run:

```bash
python scripts/migrate_add_city_to_census.py
```

- The script uses your **DATABASE_URL** from `.env` and, if you use the pooler, switches to the **direct** Supabase connection so the ALTER doesn’t hit the short timeout.
- It adds the `city` column and the index. When it finishes, confirm in **Table Editor** → **census_data** that the **city** column exists.

---

## Option B: Supabase SQL Editor (if it doesn’t timeout)

1. Go to **https://supabase.com/dashboard** → your project → **SQL Editor** → **New query**.
2. Run (one at a time if needed):

```sql
-- Add City column
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;
```

```sql
-- Index for filtering by city
CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
```

3. In **Table Editor** → **census_data**, confirm the **city** column exists.

---

## If scripts timeout: add the column in SQL Editor (one line)

1. Supabase Dashboard → **SQL Editor** → New query.
2. Paste and run **only** this (usually finishes quickly):

```sql
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;
```

3. Confirm in **Table Editor** → **census_data** that the **city** column exists.

---

## After the column exists

The app will use `city` once we populate it (next step: map city to each zip).
