# 🔍 How to View Debug Output

## Quick Method: Restart Flask in Terminal

1. **Open a new terminal/PowerShell window**
2. **Navigate to your project folder:**
   ```powershell
   cd "c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"
   ```

3. **Start Flask:**
   ```powershell
   python app.py
   ```

4. **You'll see output like:**
   ```
   * Running on http://0.0.0.0:5000
   * Debug mode: on
   ```

5. **When you test an address, you'll see `[DEBUG]` messages in this terminal**

---

## What to Look For

When you enter an address, you should see:

```
[DEBUG] get_schools_by_address: address=1010 kenliworth ave charlotte nc, lat=35.xxx, lng=-80.xxx
[DEBUG] STEP 1: Trying attendance zones (point-in-polygon)...
[DEBUG] find_zoned_schools: Testing 3528 elementary zones for point (35.xxx, -80.xxx)
[DEBUG] Attendance zones result: True/False
[DEBUG] STEP 2: ... (if zones failed)
[DEBUG] FINAL RESULT: use_zones = True/False
```

---

## Alternative: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the **Console** tab
3. Look for any JavaScript errors or API response logs

---

## If Flask Won't Start

Make sure you're in the right directory and have the dependencies installed:

```powershell
pip install -r requirements.txt
python app.py
```
