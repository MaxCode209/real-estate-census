create extension if not exists "pgcrypto";

create table if not exists public.county_employers (
    id uuid primary key default gen_random_uuid(),
    county_name text not null,
    state_code text not null default 'NC',
    county_fips text,
    year integer not null,
    month integer,
    company_name text not null,
    industry text,
    sector_class text check (sector_class in ('private_sector', 'public_sector')),
    employment_range text not null,
    rank integer not null,
    avg_salary integer,
    employment_score_primary numeric,
    employment_score_secondary numeric,
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    constraint county_employers_unique unique (county_name, year, company_name, rank)
);

comment on table public.county_employers is 'NC top employers dataset rows (county + employer + salary)';
