# Add City Column via Supabase SQL Editor (IPv4 workaround)

Your project's **Direct connection** is "Not IPv4 compatible," so from an IPv4 network the direct host won't work. Use the **SQL Editor** in the dashboard instead — it often uses a different connection/timeout.

## Step-by-step

### 1. Open SQL Editor
- In the Supabase dashboard **left sidebar**, click **"SQL Editor"** (not "Table Editor").
- Click **"New query"** (or the + tab) so you have a blank editor.

### 2. Run the ALTER (add the column)
- Paste **only** this line into the editor:
  ```sql
  ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;
  ```
- Click **"Run"** (or press Ctrl+Enter / Cmd+Enter).
- Wait for it to finish. If you see "Success" and no timeout, the column is added.

### 3. Run the index (optional but recommended)
- Clear the editor or start a **new query**.
- Paste:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
  ```
- Click **"Run"** again.

### 4. Confirm
- In the left sidebar, open **Table Editor** → **census_data**.
- You should see a new column **city** (nullable text).

---

## If the ALTER times out in SQL Editor too

- Try again during low traffic, or run only the ALTER (no SET, no index in the same run).
- Or **Supabase → Project Settings → Database**: check if there’s a way to increase statement timeout for the project.
- Or purchase the **IPv4 add-on** for the project so the Direct connection works from your network; then use the direct URL in `.env` and run `python scripts/migrate_add_city_to_census.py`.

## After the column exists

- Switch `.env` back to your **pooler** URL for normal app use (so the rest of the app and scripts use the pooler).
- Populate `city` with e.g. `python scripts/fetch_city_for_zips.py` or the CSV workflow in **CITY_COLUMN_GUIDE.md**.
