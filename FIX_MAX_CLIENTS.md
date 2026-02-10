# Fix: "Max clients reached" / "Not IPv4 compatible"

**If you see "Not IPv4 compatible"** on Direct connection, use the **Shared Pooler** (your network is IPv4; the pooler works from IPv4).

**If you see "max clients reached"**, use **Transaction mode** (port 6543) so the app doesn’t hold connections.

## What to do on the Supabase "Connect to your project" page

1. Leave **Type** = URI and **Source** = Primary Database.
2. Open the **Method** dropdown (it currently says "Direct connection").
3. Choose **Session** or **Transaction** or **Shared Pooler** (whatever options you see).
4. Prefer the one whose URI has **port 6543** (Transaction mode) – best for the app. If you only see one pooler URI (e.g. port 5432), use that.
5. Copy the **full URI** shown (replace `[YOUR-PASSWORD]` with your real database password).
6. In your project folder, open **.env** and set:
   ```env
   DATABASE_URL=<paste that URI>
   ```
7. Save `.env`, then restart your Flask app (stop it and run `python app.py` again).

Using the pooler (not Direct) avoids IPv4 issues. Using port **6543** (Transaction mode) avoids "max clients" by releasing connections after each request.

## Optional: Run the city-column migration when the pool is free

- Close the Flask app and any other tools using the database.
- Run: `python scripts/migrate_add_city_to_census.py`.
- Or run the `ALTER TABLE` in **Supabase SQL Editor** (one short query usually doesn’t time out).
- Then start the app again with the pooler URI in `.env`.
