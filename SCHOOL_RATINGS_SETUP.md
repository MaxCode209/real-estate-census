# School Ratings Integration - Setup Complete! 🎓

## What Was Implemented

I've successfully integrated **Apify Zillow School Scraper** to fetch and display school ratings (1-10 scale) for addresses in your application.

### Features Added:

1. **Database Model** (`SchoolData`)
   - Stores elementary, middle, and high school ratings
   - Stores school names and addresses
   - Calculates and stores blended school score (average of all three)
   - Caches results by address/coordinates for faster retrieval

2. **Apify Integration** (`backend/apify_client.py`)
   - Connects to Apify Zillow School Scraper API
   - Fetches schools within geographic boundaries
   - Filters by school level (elementary/middle/high)
   - Finds closest schools to an address

3. **API Endpoints**
   - `GET /api/schools/address?address=<address>&lat=<lat>&lng=<lng>`
     - Fetches school ratings for an address
     - Caches results in database
     - Returns elementary, middle, high school ratings and blended score

4. **Frontend Display**
   - New "School Scores" section in the control panel
   - Shows elementary, middle, and high school ratings (out of 10)
   - Displays school names
   - Shows blended score (average of all three)
   - Automatically appears when you search by address

## How It Works

1. **User searches by address** → Address is geocoded
2. **System fetches school data** → Calls Apify API with geographic bounds
3. **Finds closest schools** → Filters by level (elementary/middle/high)
4. **Calculates blended score** → Averages the three school ratings
5. **Displays results** → Shows in the School Scores section
6. **Caches data** → Stores in database for faster future lookups

## Configuration

Your Apify API token should be added to:
- `.env` file: `APIFY_API_TOKEN=your_apify_token_here`
- `config/config.py`: Loads the token automatically

## Database Schema

The `school_data` table includes:
- `address`, `zip_code`, `latitude`, `longitude`
- `elementary_school_name`, `elementary_school_rating`, `elementary_school_address`
- `middle_school_name`, `middle_school_rating`, `middle_school_address`
- `high_school_name`, `high_school_rating`, `high_school_address`
- `blended_school_score` (calculated average)

## Testing

To test the integration:

1. **Start your Flask app**: `python app.py`
2. **Open**: http://localhost:5000
3. **Enter an address** in the "Search Address" field (e.g., "123 Main St, New York, NY")
4. **Click "Go"**
5. **Check the "School Scores" section** - it should appear below the Info section

## Pricing

- **Apify Zillow School Scraper**: $20 per 1,000 results ($0.02 per school)
- **Free trial**: $5 credit included with Apify account
- **Caching**: Results are cached in your database, so you only pay once per address

## Troubleshooting

### School scores not appearing?
- Check browser console for errors
- Verify Apify API token is correct in `.env`
- Check that the address geocoding succeeded
- Apify scraping can take 30-60 seconds, be patient

### "Error fetching school data"?
- Verify your Apify account has credits
- Check Apify API token is valid
- Ensure the address is in the US (Zillow data is US-only)

### Database errors?
- Run database migration: The `school_data` table will be created automatically on first run
- Check your Supabase connection in `.env`

## Next Steps

The integration is complete and ready to use! When users search by address, they'll automatically see:
- Elementary school rating (1-10)
- Middle school rating (1-10)
- High school rating (1-10)
- Blended score (average of all three)

All data is cached in your database for fast retrieval on subsequent searches.
