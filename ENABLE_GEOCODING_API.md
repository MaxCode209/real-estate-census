# Enable Google Geocoding API

The geocoding feature requires the **Geocoding API** to be enabled in your Google Cloud Console.

## Quick Steps

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Select your project** (the one with your Maps API key)

3. **Navigate to APIs & Services**:
   - Click the hamburger menu (☰) in the top left
   - Go to **"APIs & Services"** → **"Library"**

4. **Search for "Geocoding API"**

5. **Click on "Geocoding API"**

6. **Click "Enable"**

7. **Wait 1-2 minutes** for the API to activate

8. **Refresh your application** and try searching for a zip code again

## Alternative: Use Backend Geocoding

I've also added a backend geocoding endpoint (`/api/geocode-zip/<zip_code>`) that uses your server-side API key. This should work even if frontend geocoding has restrictions.

The application will automatically try:
1. Frontend geocoding (if enabled)
2. Backend geocoding (fallback)
3. Show helpful error message if both fail

## Verify It's Working

After enabling, try searching for zip code `28204` (Charlotte, NC) again. It should work now!

## Cost

- **Geocoding API**: Free tier includes $200/month credit
- **$5 per 1,000 requests** after free tier
- For most use cases, the free tier is more than enough

