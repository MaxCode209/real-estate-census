# Quick Access Links

## 🗺️ View Your Map Application

**Local URL**: http://localhost:5000

Open this in your browser to see:
- Interactive Google Map with your 1,224 zip codes
- Census data visualization (Population, Income, Age)
- Search and filter functionality
- Data layers and controls

---

## 📊 View Your Database in Supabase

### Step 1: Access Supabase Dashboard
**URL**: https://supabase.com/dashboard

### Step 2: View Your Data
1. **Select your project** (the one we created)
2. Click **"Table Editor"** in the left sidebar
3. Click on **`census_data`** table

You'll see a spreadsheet-like view with all your data:
- zip_code
- population
- median_age
- average_household_income (AHHI)
- state
- county
- data_year
- created_at
- updated_at

### Step 3: Query Your Data (Optional)
Click **"SQL Editor"** in the left sidebar and run:

```sql
SELECT 
  zip_code,
  state,
  population,
  median_age,
  average_household_income,
  data_year
FROM census_data
ORDER BY zip_code;
```

### Export to Excel/CSV
In Table Editor, click the **download/export** button to get a CSV file.

---

## 📈 Current Database Stats

- **Total Records**: 1,224 zip codes
- **Data Includes**: Population, Median Age, Average Household Income
- **Database**: Supabase Cloud PostgreSQL (FREE tier)
- **Location**: Cloud-hosted, accessible from anywhere

---

## 🔗 Quick Links

- **Map Application**: http://localhost:5000
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Your Project**: Look for project with database: `db.naixizrmldynltbaioem.supabase.co`
