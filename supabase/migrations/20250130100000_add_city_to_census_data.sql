-- Allow up to 5 minutes for ALTER/INDEX on large tables (avoids statement timeout)
SET statement_timeout = '300s';

-- Add city column to census_data (for future "Search by City" or market features)
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;

-- Index for filtering/lookups by city
CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
