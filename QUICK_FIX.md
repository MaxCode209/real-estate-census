# Troubleshooting Localhost Error

## Common Issues & Solutions

### 1. "This site can't be reached" or "Connection refused"
**Solution**: Make sure Flask is running
```bash
python app.py
```
You should see: `Running on http://127.0.0.1:5000`

### 2. Page loads but map is blank
**Possible causes**:
- Google Maps API key issue
- JavaScript console errors
- Check browser console (F12) for errors

### 3. "404 Not Found"
**Solution**: Make sure you're accessing: `http://localhost:5000` (not port 5001 or other)

### 4. Port already in use
**Solution**: Kill the process using port 5000
```bash
# Find process
netstat -ano | findstr :5000

# Kill it (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## Quick Test

1. **Check if Flask is running**:
   - Look for Python process in Task Manager
   - Or run: `netstat -ano | findstr :5000`

2. **Test API directly**:
   - Open: http://localhost:5000/api/census-data
   - Should return JSON with census data

3. **Check browser console**:
   - Press F12
   - Go to Console tab
   - Look for red error messages

## Restart the App

If nothing works, restart:
1. Stop the current Flask app (Ctrl+C in terminal)
2. Run: `python app.py`
3. Wait for "Running on..." message
4. Open: http://localhost:5000

