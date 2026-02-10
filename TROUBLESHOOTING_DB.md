# Database Connection Troubleshooting

## Issue: Hostname Not Resolving

If you're getting "could not translate host name" error, try these steps:

### Step 1: Verify Your Supabase Project is Ready

1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Check your project status - it should show "Active" (not "Setting up")
3. If it's still setting up, wait 2-3 more minutes

### Step 2: Get the Correct Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Scroll to **"Connection string"** section
3. Make sure you're using **"Session mode"** (not Transaction mode)
4. Copy the connection string again
5. **Important**: Replace `[YOUR-PASSWORD]` with your actual password (no brackets!)

### Step 3: Verify Connection String Format

Your connection string should look like:
```
postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

**NOT:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

The brackets `[]` should NOT be in the actual connection string - they're just placeholders in the UI.

### Step 4: Check Network/Firewall

- Make sure you have internet connection
- Some corporate networks block database connections
- Try from a different network if possible

### Step 5: Alternative - Use Connection Pooling

If direct connection doesn't work, try the "Connection pooling" mode:
1. In Supabase dashboard → Settings → Database
2. Use **"Transaction mode"** connection string instead
3. This uses port 6543 instead of 5432

### Step 6: Verify Project Region

Make sure your project region matches where you're connecting from. If you're in the US, use a US region.

## Still Not Working?

1. Double-check the hostname in Supabase dashboard
2. Verify your password is correct
3. Check if Supabase project shows any errors
4. Try creating a new project if this one seems stuck

