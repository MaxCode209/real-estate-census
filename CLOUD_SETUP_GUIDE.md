# Cloud PostgreSQL Setup Guide

## Step-by-Step: Setting Up Supabase (Free Tier)

### Step 1: Sign Up for Supabase

1. Go to: **https://supabase.com**
2. Click **"Start your project"** or **"Sign up"**
3. Sign up with:
   - GitHub account (easiest), OR
   - Email address
4. Verify your email if needed

### Step 2: Create a New Project

1. Click **"New Project"** button
2. Fill in:
   - **Name**: `real-estate-census` (or any name you like)
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., `US East` for US)
3. Click **"Create new project"**
4. Wait 2-3 minutes for setup to complete

### Step 3: Get Your Connection String

**IMPORTANT: Use Session Pooler (IPv4 Compatible)**

1. Once project is ready, go to **Settings** (gear icon in left sidebar)
2. Click **"Database"** in the settings menu
3. Scroll down to **"Connection string"** section
4. In the **"Method"** dropdown, select **"Session Pooler"** (NOT "Direct connection")
   - Direct connection is IPv6-only and won't work on most networks
   - Session Pooler is IPv4 compatible and works everywhere
5. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:6543/postgres?pgbouncer=true
   ```
   Note: Port 6543 (pooler) instead of 5432 (direct)
6. **Replace `[YOUR-PASSWORD]`** with the password you created in Step 2

### Step 4: Test Connection (Optional)

You can test the connection string format, but we'll verify it works when we initialize the database.

---

## Alternative: ElephantSQL (Simpler, Smaller Free Tier)

If you prefer a simpler option:

1. Go to: **https://www.elephantsql.com**
2. Click **"Get a managed PostgreSQL database"**
3. Select **"Tiny Turtle"** (free tier)
4. Sign up with GitHub or email
5. Create instance (takes ~1 minute)
6. Go to your instance details
7. Copy the connection string from **"Details"** tab

---

## Next Steps After Getting Connection String

Once you have your connection string, come back and we'll:
1. Set up your `.env` file
2. Initialize the database
3. Test with sample data

**Ready?** Get your connection string and let me know when you have it!

