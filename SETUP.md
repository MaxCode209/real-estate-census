# Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL
```bash
# Create database
createdb real_estate_census

# Or using psql
psql -U postgres
CREATE DATABASE real_estate_census;
```

#### Option B: Cloud PostgreSQL (Free Options)
- **Supabase**: https://supabase.com (Free tier available)
- **ElephantSQL**: https://www.elephantsql.com (Free tier available)
- **Neon**: https://neon.tech (Free tier available)

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/real_estate_census

# Google Maps API Key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Census Bureau API Key (optional but recommended)
CENSUS_API_KEY=your_census_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Google Sheets API (for export functionality)
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/google_sheets_credentials.json
```

#### Getting API Keys:

1. **Google Maps API Key**:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable "Maps JavaScript API"
   - Create credentials (API Key)
   - Restrict the key to your domain (optional but recommended)

2. **Census Bureau API Key** (Optional):
   - Go to https://api.census.gov/data/key_signup.html
   - Sign up for a free API key
   - This helps with rate limits

3. **Google Sheets API** (For export):
   - Go to https://console.cloud.google.com/
   - Enable "Google Sheets API" and "Google Drive API"
   - Create a service account
   - Download credentials JSON file
   - Place in `credentials/google_sheets_credentials.json`

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Fetch Initial Census Data

```bash
# Fetch all zip codes (may take a while)
python scripts/fetch_census_data.py

# Or fetch specific zip codes
python scripts/fetch_census_data.py --zip-codes 10001 10002 10003

# Or limit the number of records
python scripts/fetch_census_data.py --limit 100
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Schema

The `census_data` table stores:
- `zip_code`: Zip code (primary identifier)
- `state`: State abbreviation
- `county`: County name
- `population`: Total population
- `median_age`: Median age
- `average_household_income`: Average household income (AHHI)
- `data_year`: Year of the data
- `created_at`, `updated_at`: Timestamps

## API Endpoints

- `GET /api/census-data` - Get census data (with filters)
- `GET /api/census-data/zip/<zip_code>` - Get data for specific zip code
- `POST /api/census-data` - Add/update census data
- `POST /api/census-data/bulk` - Bulk add/update
- `POST /api/census-data/fetch` - Fetch from Census API and store
- `GET /api/export/sheets` - Export to Google Sheets

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- Ensure database exists

### Census API Issues
- API key is optional but recommended for higher rate limits
- Some zip codes may not have data available
- Large requests may timeout - use `--limit` flag

### Google Maps Not Loading
- Verify API key is correct
- Check that "Maps JavaScript API" is enabled
- Check browser console for errors

### Google Sheets Export Issues
- Ensure service account credentials file exists
- Verify Google Sheets API and Drive API are enabled
- Check file path in `.env`

## Next Steps

1. **Add Zip Code Geocoding**: For better performance, consider using a zip code centroid database instead of geocoding each zip code
2. **Add Caching**: Implement caching for frequently accessed data
3. **Add More Census Variables**: Extend the model to include additional census data points
4. **Optimize Queries**: Add database indexes for common query patterns
5. **Add Authentication**: If deploying publicly, add user authentication

