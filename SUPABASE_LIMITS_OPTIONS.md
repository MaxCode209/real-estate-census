# Supabase limits – what to do when you hit "max clients" or timeouts

Your app is already using **port 6543 (Transaction mode)**. If you still see "max clients" or can’t run simple SQL in the dashboard, Supabase’s pool is full or very limited. Here are concrete options.

---

## 1. Increase pool size in Supabase (try this first)

Supabase lets you raise the pool size in the dashboard:

1. Go to **https://supabase.com/dashboard** → your project.
2. Open **Database** (left sidebar) → **Settings** (or **Project Settings** → **Database**).
3. Find **Default Pool Size** and/or **Max Client Connections**.
4. Increase them (e.g. double the default), save.
5. Close **all** other things using this project (Flask app, SQL Editor tabs, other scripts).
6. Wait ~30 seconds, then try again:
   - Start the app: `python app.py`
   - Or run one SQL in **SQL Editor**:  
     `ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;`

---

## 2. Free connections before running SQL

The dashboard (Table Editor, SQL Editor) uses Session connections (port 5432). Those count toward the same limit.

- **Stop the Flask app** (Ctrl+C).
- Close every **SQL Editor** tab and **Table Editor** tab for this project.
- Wait 1–2 minutes.
- Open **one** SQL Editor tab, run only:  
  `ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;`  
  then run it. If it still times out, try again in a few minutes or after increasing pool size (step 1).

---

## 3. New Supabase project (fresh pool)

If this project’s pool is always full:

1. Create a **new project** in Supabase (same org or new).
2. In the new project, run your schema (tables: `census_data`, `school_data`, `attendance_zones`). You can copy the schema from the old project or from your migrations.
3. Export data from the old project (e.g. CSV or `pg_dump`), import into the new one (or re-run your import scripts against the new DB).
4. In your app’s **.env**, set `DATABASE_URL` to the **new project’s** connection string (use **Transaction** mode, port **6543**).
5. Use the new project for both the app and the dashboard. You get a new pool and no leftover connections.

---

## 4. Local PostgreSQL (no Supabase limits)

Run Postgres on your machine and point the app at it for development:

1. Install PostgreSQL (e.g. from https://www.postgresql.org/download/windows/).
2. Create a database, e.g. `real_estate_census`.
3. In **.env** set:  
   `DATABASE_URL=postgresql://postgres:YOUR_LOCAL_PASSWORD@localhost:5432/real_estate_census`
4. Run your migrations or schema scripts against this DB. Re-import census/school data if needed (or use Supabase only for production later).
5. Run the app; it will use local Postgres. No Supabase connection limits or timeouts.

---

## 5. Summary

| Option | Effort | Best when |
|-------|--------|-----------|
| Increase pool size (1) | Low | You want to keep this project and just need a bit more room. |
| Free connections (2) | Low | You only need to run one ALTER or a few queries. |
| New Supabase project (3) | Medium | This project’s pool is always exhausted. |
| Local PostgreSQL (4) | Medium | You want to develop without Supabase limits. |

Recommendation: do **1** and **2** first. If SQL Editor still times out or you still hit "max clients", then try **3** or **4**.
