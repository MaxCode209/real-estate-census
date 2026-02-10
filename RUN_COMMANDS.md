# Commands to Run This Code Properly

Use this project folder:
`c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process`

---

## One-time setup

### 1. Go to the project folder
```powershell
cd "c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"
```

### 2. (Optional) Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project folder (or edit the existing one) with at least:

- **DATABASE_URL** – Supabase connection string (use **port 6543**, Transaction mode).  
  Example: `postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-us-west-2.pooler.supabase.com:6543/postgres`
- **GOOGLE_MAPS_API_KEY** – For the map.
- **CENSUS_API_KEY** – Optional but recommended for census data.
- **APIFY_API_TOKEN** – For school ratings (if you use that feature).

See `.env` or project docs for other optional keys.

### 5. (Optional) Test database connection
```powershell
python scripts/test_db_connection.py
```

### 6. (Optional) Bulk import census data (one-time, ~5–15 min)
Only if your Supabase `census_data` table is empty or you want to refresh:

```powershell
python scripts/bulk_import_all_census_data.py
```

---

## Run the application

### Start the app
```powershell
cd "c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"
python app.py
```

You should see something like:
- `[App] Running from: ...\Data Site Selection Process`
- `[DB] Using Supabase pooler port 6543 (Transaction mode) - OK`
- `Running on http://127.0.0.1:5000`

### Open the map
In your browser go to: **http://localhost:5000**

### Stop the app
In the terminal where it’s running: **Ctrl+C**

---

## Quick reference

| What | Command |
|------|--------|
| **Start app** | `python app.py` |
| **Map** | http://localhost:5000 |
| **Supabase** | https://supabase.com/dashboard |
| **Test DB** | `python scripts/test_db_connection.py` |
| **Bulk import census** | `python scripts/bulk_import_all_census_data.py` |
| **Export attendance zones** | `python scripts/export_attendance_zones.py` |

---

## If you get “max clients” or connection errors

- Use **port 6543** (Transaction mode) in `DATABASE_URL`, not 5432.
- See **FIX_MAX_CLIENTS.md** and **SUPABASE_LIMITS_OPTIONS.md** for Supabase limits and fixes.
