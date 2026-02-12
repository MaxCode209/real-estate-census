-- Add state column for city+state search (e.g. Wilmington NC vs Wilmington DE)
-- Run in Supabase SQL Editor; if timeout occurs, run just the ALTER first.

ALTER TABLE census_data ADD COLUMN IF NOT EXISTS state VARCHAR(2);
