-- Canonical schools table: one row per unique school with address, lat/lng, rating
CREATE TABLE IF NOT EXISTS schools (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  level VARCHAR(50) NOT NULL,
  address VARCHAR(500),
  city VARCHAR(100),
  state VARCHAR(2),
  zip_code VARCHAR(10),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  rating DOUBLE PRECISION,
  nces_id VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_schools_name_level ON schools(name, level);
CREATE INDEX IF NOT EXISTS idx_schools_zip ON schools(zip_code);
CREATE INDEX IF NOT EXISTS idx_schools_location ON schools(latitude, longitude);
