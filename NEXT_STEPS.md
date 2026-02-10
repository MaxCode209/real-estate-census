# Next Steps - Setup Checklist

## ✅ Completed
- [x] Python 3.12.5 is installed
- [x] All Python dependencies installed (Flask, PostgreSQL driver, etc.)

## 🔲 Still Needed

### 1. Set Up Database (Choose ONE option)

#### Option A: Cloud PostgreSQL (Easiest - Recommended)
**Free options:**
- **Supabase**: https://supabase.com (Free tier: 500MB database)
- **ElephantSQL**: https://www.elephantsql.com (Free tier: 20MB database)
- **Neon**: https://neon.tech (Free tier available)

**Steps:**
1. Sign up for one of the services above
2. Create a new database
3. Copy the connection string (looks like: `postgresql://user:password@host:port/database`)

#### Option B: Install PostgreSQL Locally
1. Download from: https://www.postgresql.org/download/windows/
2. Install PostgreSQL
3. Create database: `createdb real_estate_census`
4. Connection string: `postgresql://postgres:your_password@localhost:5432/real_estate_census`

### 2. Get API Keys

#### Google Maps API Key (REQUIRED)
1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "Maps JavaScript API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key

#### Census Bureau API Key (Optional but Recommended)
1. Go to: https://api.census.gov/data/key_signup.html
2. Sign up for free API key
3. Copy the key (helps with rate limits)

### 3. Configure Environment

Run the setup script:
```bash
python scripts/setup_env.py
```

Or manually create a `.env` file with:
```env
DATABASE_URL=postgresql://your_connection_string_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
CENSUS_API_KEY=your_census_key_here
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=any_random_string_here
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/google_sheets_credentials.json
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Fetch Some Test Data

```bash
# Fetch a few zip codes to test
python scripts/fetch_census_data.py --zip-codes 10001 10002 10003 90210 60601

# Or fetch more (limit to 100 for testing)
python scripts/fetch_census_data.py --limit 100
```

### 6. Run the Application

```bash
python app.py
```

Then open: http://localhost:5000

## Quick Start (If you have everything ready)

```bash
# 1. Set up environment
python scripts/setup_env.py

# 2. Initialize database
python scripts/init_db.py

# 3. Fetch test data
python scripts/fetch_census_data.py --limit 50

# 4. Run app
python app.py
```

## Need Help?

- See `SETUP.md` for detailed instructions
- See `README.md` for project overview
- Check `examples/api_usage.py` for API examples

