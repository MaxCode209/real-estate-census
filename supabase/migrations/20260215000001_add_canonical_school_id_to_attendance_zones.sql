-- Link attendance zones to canonical schools table for direct join
ALTER TABLE attendance_zones
ADD COLUMN IF NOT EXISTS canonical_school_id INTEGER REFERENCES schools(id);

CREATE INDEX IF NOT EXISTS idx_attendance_zones_canonical_school ON attendance_zones(canonical_school_id);
