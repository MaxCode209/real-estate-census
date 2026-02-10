# Troubleshooting School Scores Showing N/A

## Quick Checks

1. **Open Browser Console** (F12 or Right-click → Inspect → Console tab)
   - Look for any red error messages
   - Check for messages like "Fetching school data for: ..."
   - Check for "Response status: ..." and "School data received: ..."

2. **Check Flask Server Logs**
   - Look for "DEBUG: Fetching school data for address: ..."
   - Look for "DEBUG: Apify input data: ..."
   - Look for any error messages

3. **Common Issues:**

### Issue 1: Apify API Timeout
- **Symptom**: School scores show "N/A" after 30-60 seconds
- **Cause**: Apify scraping takes time, browser might timeout
- **Solution**: I've increased the timeout to 2 minutes. If it still times out, check server logs.

### Issue 2: No Schools Found
- **Symptom**: All scores show "N/A" with "No data available"
- **Cause**: Apify didn't find schools in the area, or API call failed
- **Check**: Look in browser console for "School data received:" - what does it show?

### Issue 3: Server Not Restarted
- **Symptom**: Changes not taking effect
- **Solution**: Restart Flask server (I just did this for you)

## Testing Steps

1. **Search for an address** (e.g., "123 Main St, Charlotte, NC")
2. **Open browser console** (F12)
3. **Watch for these messages:**
   - "Fetching school data for: ..."
   - "Response status: 200" (or other status)
   - "School data received: {...}"
4. **Check what data is received** - copy the "School data received:" object

## What to Look For

In the browser console, after searching an address, you should see:
```
Fetching school data for: [address] ([lat], [lng])
Response status: 200
School data received: {elementary_school_rating: ..., middle_school_rating: ..., ...}
```

If you see:
- `Response status: 500` → Server error, check Flask logs
- `Response status: 200` but all ratings are `null` → Apify didn't find schools
- `Request timed out` → Apify is taking too long (normal, can take 30-60 seconds)

## Next Steps

1. Try searching for an address
2. Open browser console (F12)
3. Share what you see in the console, especially:
   - The "School data received:" object
   - Any error messages
   - The response status

This will help me diagnose the exact issue!
