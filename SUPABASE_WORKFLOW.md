# How We Work With Supabase (Historically vs Now)

## How We Did It Historically

1. **Schema in code**  
   - **`backend/models.py`** — single source of truth for table/column definitions (CensusData, SchoolData, etc.).  
   - When we added columns before (e.g. `total_households`, `owner_occupied_units`), we used **Python migration scripts** like `scripts/migrate_census_schema.py` that connect with your `DATABASE_URL` and run `ALTER TABLE ... ADD COLUMN ...`.

2. **Seeing data / columns**  
   - I don’t have direct access to your Supabase project.  
   - We worked together by:  
     - **You** using Supabase Dashboard → Table Editor or SQL Editor (see **VIEW_SUPABASE_DATA.md**).  
     - **You** running scripts that query the DB and sharing the output (or we relied on `models.py` and docs).  
   - So “seeing” and “modifying together” meant: I write the migration/SQL and docs, you run them and use the Dashboard; we keep schema in code.

3. **Why those migrations worked then**  
   - Same flow: Python script + `DATABASE_URL` (pooler or direct).  
   - They likely succeeded because: the table was smaller, Supabase had a longer timeout, or there was less lock contention.  
   - Nothing special about “how” we did it — we just didn’t hit the pooler timeout before.

---

## Why the City Column Fails Now

- **Supabase pooler** (e.g. `aws-0-us-west-2.pooler.supabase.com`) enforces a **short statement timeout** (often ~8 seconds).  
- **`ALTER TABLE census_data ADD COLUMN city ...`** is being **canceled by that timeout** (either the ALTER or lock wait takes longer than the limit).  
- **Direct connection** (`db.naixizrmldynltbaioem.supabase.co:5432`) would bypass the pooler and usually has no such short limit — but on your machine the script reported **“Direct host unreachable”**, so it fell back to the pooler and hit the same timeout again.

So we *are* doing it the same way (Python migration + `DATABASE_URL`); the difference is **pooler timeout** and **direct host not reachable** from your current network.

---

## Optimal Setup: Code, Data, and Schema in One Flow

Goal: push code and schema changes from the app/repo and run migrations without timeouts.

| What | Where | How |
|------|--------|-----|
| **Schema (source of truth)** | `backend/models.py` + `supabase/migrations/*.sql` | Models define tables; migrations apply DDL. |
| **Applying migrations** | Your machine or CI | Prefer **direct** DB URL for DDL so the pooler doesn’t kill long statements. |
| **Viewing / inspecting data** | You in Dashboard, or script output you share | Run `python scripts/describe_census_schema.py` (or similar) and paste output so we can reason about columns and data. |
| **Data changes** | Scripts (e.g. `fetch_census_data.py`, `assign_city_from_csv.py`) | Use normal `DATABASE_URL`; these are many short statements, not one long ALTER. |

Concrete workflow:

1. **Schema change**  
   - Add column to `models.py` (e.g. `city` — already there).  
   - Add a migration: either a file under `supabase/migrations/` (then `npx supabase db push`) or a Python migration script.

2. **Run the migration**  
   - Use a **direct** connection so the pooler doesn’t timeout:  
     - In **`.env`**: set `DATABASE_URL` (or a dedicated `DATABASE_URL_DIRECT`) to the **Direct** URI from Supabase (Dashboard → Project Settings → Database → Connection string → **Direct**, host `db.xxx.supabase.co`, port 5432).  
     - Run the migration script (or `supabase db push`).  
   - If the direct host is unreachable from your machine (DNS/firewall), fix that first (e.g. `scripts/check_supabase_setup.py`, different network, or Supabase’s exact Direct URI).

3. **Inspecting schema/data together**  
   - You run: `python scripts/describe_census_schema.py`  
   - You paste the output here.  
   - I use that to confirm columns (e.g. that `city` exists and how data looks) and suggest next steps.

4. **Normal app and data scripts**  
   - Keep using your usual `DATABASE_URL` (pooler is fine for normal queries and bulk data scripts).

---

## Fixing the City Column Right Now

Pick one path:

### Option A: Use Direct Connection (best long-term)

1. In Supabase: **Project Settings → Database**. Under **Connection string**, choose the **Direct** (or Session) URI: host `db.naixizrmldynltbaioem.supabase.co`, port **5432** (not the pooler URL).  
2. In **`.env`**, set `DATABASE_URL` to that **full** Direct URI (same user/password as now).  
3. On your machine, run: `python scripts/check_supabase_setup.py`  
   - If it says DNS/port OK, run: `python scripts/migrate_add_city_to_census.py`  
   - If “Direct host unreachable”, try another network or VPN; the direct host must be reachable from where you run the script.

### Option B: Run ALTER in Supabase SQL Editor

1. Supabase Dashboard → **SQL Editor**.  
2. Run **only** this (one statement):  
   `ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;`  
3. If it still times out, try again during low traffic, or use Option A/C.

### Option C: Ask Supabase to Increase Timeout

Some plans let you set `statement_timeout` (e.g. in Dashboard or via support). If they increase it for your project, the same Python migration over the pooler might succeed.

---

## Summary

- **Historically:** We never had direct DB access. We defined schema in code, wrote migrations and docs, and you ran them and used the Dashboard; that’s why it felt like we were “seeing and modifying together.”  
- **Now:** Same idea, but the **pooler’s statement timeout** kills the ALTER, and the **direct host is unreachable** from your current setup, so the script falls back to the pooler and fails again.  
- **Optimal setup:** Keep schema in `models.py` and migrations; run DDL over a **direct** connection; use a small **describe** script and shared output so we can inspect schema and data without me connecting to Supabase.  
- **Immediate fix for `city`:** Get the **Direct** connection working (Option A) and run the migration script, or run the single ALTER in the SQL Editor (Option B), or have Supabase raise the timeout (Option C).
