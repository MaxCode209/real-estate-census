alter table if exists public.county_employers
    drop column if exists employment_score_primary,
    drop column if exists employment_score_secondary;
