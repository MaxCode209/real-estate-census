-- Run this in Supabase Dashboard → SQL Editor (avoids statement timeout from the pooler).
-- Adds 'city' column to census_data for "Search by City" / market.

ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;

CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city);
