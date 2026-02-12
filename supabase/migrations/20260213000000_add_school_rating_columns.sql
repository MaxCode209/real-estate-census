-- Add average school rating columns by level for census_data
-- Run this in Supabase Dashboard -> SQL Editor if migrations timeout
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS average_elementary_school_rating double precision;
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS average_middle_school_rating double precision;
ALTER TABLE census_data ADD COLUMN IF NOT EXISTS average_high_school_rating double precision;
