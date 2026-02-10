# Add City Column to Census Data — Step by Step

Use the **Supabase CLI** so the migration runs against your database without hitting the SQL Editor timeout.

---

## Step 1: Open terminal in your project folder

- In VS Code / Cursor: **Terminal → New Terminal**
- Or open PowerShell/Command Prompt and `cd` to:
  `...\Data Site Selection Process`

---

## Step 2: Link your project to Supabase

Run (use your project ref; the one you found is below):

```bash
supabase link --project-ref naixizrmldynltbaioem
```

- If prompted, log in (browser or token).
- This creates/updates `supabase/config.toml` and links this folder to that project.

---

## Step 3: Create a new migration (optional — file already added)

A migration file is already in this repo:

- **File:** `supabase/migrations/20250130100000_add_city_to_census_data.sql`

If you prefer to create it via the CLI instead:

```bash
supabase migration new add_city_to_census_data
```

That creates a new file like `supabase/migrations/YYYYMMDDHHMMSS_add_city_to_census_data.sql`.  
**Open that file** and replace its contents with:

```sql
-- Add city column to census_data (for future "Search by City" or market features)
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;

-- Index for filtering/lookups by city
CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
```

If you use the **existing** file (`20250130100000_add_city_to_census_data.sql`), you can skip creating another one.

---

## Step 4: Apply the migration to your database

Run:

```bash
supabase db push
```

- This applies all pending migrations in `supabase/migrations/` to the linked project.
- You should see something like: `Applying migration 20250130100000_add_city_to_census_data.sql` and then success.

---

## Step 5: Confirm in Supabase

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your project.
2. Go to **Table Editor** → open the **census_data** table.
3. You should see a new column **city** (nullable text).

---

## If you get "statement timeout" on `db push`

Supabase can enforce a short timeout even for migrations. Try this **fallback**:

1. **Get the Direct connection URI**  
   Supabase Dashboard → **Project Settings** → **Database** → **Connection string** → open the dropdown and copy the **URI** for the **Direct** connection (host like `db.xxxx.supabase.co`, **port 5432** — not the pooler on 6543).

2. **Put it in `.env`**  
   Set `DATABASE_URL` to that full URI (replace any existing `DATABASE_URL` for this run).

3. **Run the Python migration** (uses direct connection and a 5‑minute timeout):
   ```bash
   python scripts/migrate_add_city_to_census.py
   ```

4. **So `db push` doesn’t retry the failed migration**  
   Either:
   - **Option A:** Remove the migration file so it’s not applied again:
     - Delete or move `supabase/migrations/20250130100000_add_city_to_census_data.sql`
     - Next time you run `db push`, this migration won’t run (the column is already there).
   - **Option B:** If your project tracks applied migrations in a table, mark this one as applied (e.g. insert `20250130100000` into that table) so `db push` skips it.

---

## If something else goes wrong

- **“Project not linked”**  
  Run Step 2 again from the project folder.

- **“No migrations to push”**  
  Either the migration was already applied, or the migration file is not in `supabase/migrations/`.  
  Check that `supabase/migrations/20250130100000_add_city_to_census_data.sql` exists and has the SQL above.

- **“Migration failed” (other errors)**  
  Copy the error message. If the column already exists, that’s fine; the migration uses `IF NOT EXISTS` so it’s safe to fix the migration and try again, or mark it as applied.

---

## After the column exists

You can populate `city` per zip using:

- `python scripts/fetch_city_for_zips.py` (Zippopotam.us API), or  
- `scripts/export_zips_for_city.py` → edit CSV → `scripts/assign_city_from_csv.py`

See **CITY_COLUMN_GUIDE.md** for details.
