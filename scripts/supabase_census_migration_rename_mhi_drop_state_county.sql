-- Run this ONCE in Supabase SQL Editor before running the census refresh.
-- 1. Rename average_household_income -> median_household_income
-- 2. Drop state and county columns

ALTER TABLE census_data
  RENAME COLUMN average_household_income TO median_household_income;

ALTER TABLE census_data DROP COLUMN IF EXISTS state;
ALTER TABLE census_data DROP COLUMN IF EXISTS county;
