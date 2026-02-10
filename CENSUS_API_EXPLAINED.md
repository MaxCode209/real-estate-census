# Census Bureau API - How It Works

## Good News: It's FREE! 🎉

The **US Census Bureau API is completely free** and **does NOT require an API key** for basic usage!

## Why No API Key Was Needed

### 1. **Census API is Public & Free**
- The US Census Bureau provides public data for free
- No registration required for basic access
- No tokens, no credits, no costs

### 2. **API Key is Optional**
Looking at the code (`backend/census_api.py` line 28):
```python
'key': self.api_key if self.api_key else ''
```

This means:
- ✅ **Without API key**: Works fine, but has **lower rate limits** (500 requests/day)
- ✅ **With API key**: Higher rate limits (5,000 requests/day)

### 3. **Rate Limits**

**Without API Key:**
- 500 requests per day
- 50 variables per request
- Slower for bulk data fetching

**With API Key (Free):**
- 5,000 requests per day
- 50 variables per request
- Better for fetching lots of data

## Cost Comparison

| Service | Cost | API Key Required? |
|---------|------|-------------------|
| **Census Bureau API** | **FREE** | Optional (free key) |
| Google Maps API | Free tier, then pay-per-use | ✅ Required |
| Supabase Database | Free tier available | ✅ Required |

## Should You Get a Census API Key?

### Get a Key If:
- ✅ You plan to fetch data for 100+ zip codes
- ✅ You'll be making frequent requests
- ✅ You want faster, more reliable access

### You Don't Need a Key If:
- ✅ You're just testing with a few zip codes
- ✅ You're fetching data occasionally
- ✅ 500 requests/day is enough for you

## How to Get a Free Census API Key (Optional)

1. Go to: https://api.census.gov/data/key_signup.html
2. Fill out the form (takes 30 seconds)
3. You'll get an email with your API key
4. Add it to your `.env` file:
   ```
   CENSUS_API_KEY=your_key_here
   ```

## What We Fetched Without a Key

When we ran:
```bash
python scripts/fetch_census_data.py --zip-codes 10001 10002 10003 90210 60601
```

This made **5 API requests** (one per zip code), which is well within the 500/day limit.

## Summary

- ✅ **Census API is FREE** - no cost, ever
- ✅ **No API key required** - works without one
- ✅ **API key is optional** - only needed for higher rate limits
- ✅ **No tokens/credits** - unlimited free access (within rate limits)

You can fetch census data all day long without spending a penny! 🎉

