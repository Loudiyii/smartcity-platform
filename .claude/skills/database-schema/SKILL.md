# Skill: Database Schema (Supabase/PostgreSQL)

## Purpose
Design and maintain the database schema, optimize queries, implement Row Level Security (RLS), and write SQL functions for the Smart City platform using Supabase (PostgreSQL 17).

## When to Use
- Creating or modifying database tables
- Writing complex SQL queries
- Implementing RLS policies
- Creating SQL functions and triggers
- Optimizing database performance with indexes
- Migrating database schema

## Supabase Configuration

**Project Details:**
- Project ID: vnznhsbjqxufvhasotid
- Region: eu-central-2 (Frankfurt)
- PostgreSQL Version: 17.6.1
- URL: https://vnznhsbjqxufvhasotid.supabase.co

## Database Schema

### 1. air_quality_measurements

Primary table for storing air quality data from APIs and IoT sensors.

```sql
CREATE TABLE air_quality_measurements (
  id BIGSERIAL PRIMARY KEY,
  source VARCHAR(50) NOT NULL,           -- 'api' or 'sensor_xxx'
  city VARCHAR(100),
  location JSONB,                        -- {lat, lon, name}

  -- Pollutants (μg/m³)
  aqi INTEGER CHECK (aqi >= 0 AND aqi <= 500),
  pm25 REAL CHECK (pm25 >= 0),
  pm10 REAL CHECK (pm10 >= 0),
  no2 REAL CHECK (no2 >= 0),
  o3 REAL CHECK (o3 >= 0),
  so2 REAL CHECK (so2 >= 0),

  -- Metadata
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_timestamp_source ON air_quality_measurements(timestamp DESC, source);
CREATE INDEX idx_city_timestamp ON air_quality_measurements(city, timestamp DESC);
CREATE INDEX idx_source ON air_quality_measurements(source);
CREATE INDEX idx_location ON air_quality_measurements USING GIN (location);

-- Comments
COMMENT ON TABLE air_quality_measurements IS 'Time-series air quality data from API and IoT sensors';
COMMENT ON COLUMN air_quality_measurements.source IS 'Data source: api or sensor_xxx';
COMMENT ON COLUMN air_quality_measurements.location IS 'GeoJSON point: {"lat": 48.86, "lon": 2.35, "name": "Paris"}';
```

### 2. weather_data

Meteorological data for correlation with air quality.

```sql
CREATE TABLE weather_data (
  id BIGSERIAL PRIMARY KEY,
  city VARCHAR(100) NOT NULL,

  -- Weather metrics
  temperature REAL NOT NULL,
  humidity INTEGER CHECK (humidity BETWEEN 0 AND 100),
  pressure INTEGER CHECK (pressure > 0),
  wind_speed REAL CHECK (wind_speed >= 0),
  wind_direction INTEGER CHECK (wind_direction BETWEEN 0 AND 360),

  -- Metadata
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_weather_city_timestamp ON weather_data(city, timestamp DESC);

COMMENT ON TABLE weather_data IS 'Weather data from OpenWeatherMap API';
```

### 3. predictions

ML model predictions for future air quality.

```sql
CREATE TABLE predictions (
  id BIGSERIAL PRIMARY KEY,
  pollutant VARCHAR(20) NOT NULL,        -- 'pm25', 'pm10', 'no2', etc.
  predicted_value REAL NOT NULL CHECK (predicted_value >= 0),
  confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 1),

  -- Prediction metadata
  prediction_for_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Model info
  model_version VARCHAR(50),
  model_accuracy REAL,

  CONSTRAINT unique_prediction_per_day UNIQUE (pollutant, prediction_for_date)
);

CREATE INDEX idx_predictions_date ON predictions(prediction_for_date DESC);
CREATE INDEX idx_predictions_pollutant ON predictions(pollutant, prediction_for_date DESC);

COMMENT ON TABLE predictions IS 'AI/ML predictions for next-day air quality';
```

### 4. sensor_metadata

IoT sensor configuration and status.

```sql
CREATE TABLE sensor_metadata (
  sensor_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  location JSONB NOT NULL,               -- {lat, lon, address}
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'offline')),
  last_reading_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sensor_location ON sensor_metadata USING GIN (location);
CREATE INDEX idx_sensor_status ON sensor_metadata(status);

COMMENT ON TABLE sensor_metadata IS 'IoT sensor registry and status';
```

### 5. alerts

System-generated alerts for threshold exceedances and anomalies.

```sql
CREATE TABLE alerts (
  id BIGSERIAL PRIMARY KEY,
  alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('threshold_exceeded', 'anomaly_detected', 'sensor_offline')),
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),

  -- Alert details
  pollutant VARCHAR(20),
  value REAL,
  threshold REAL,
  message TEXT,

  -- Status
  sent_at TIMESTAMPTZ,
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by VARCHAR(100),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);

COMMENT ON TABLE alerts IS 'System alerts for pollution events and sensor issues';
```

## SQL Functions

### 1. Average PM2.5 Calculation

```sql
CREATE OR REPLACE FUNCTION get_average_pm25(hours INTEGER DEFAULT 24)
RETURNS REAL AS $$
BEGIN
  RETURN (
    SELECT COALESCE(AVG(pm25), 0)
    FROM air_quality_measurements
    WHERE timestamp >= NOW() - INTERVAL '1 hour' * hours
      AND pm25 IS NOT NULL
  );
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT get_average_pm25(24);  -- 24-hour average
SELECT get_average_pm25(168); -- 7-day average
```

### 2. Anomaly Detection (Z-Score)

```sql
CREATE OR REPLACE FUNCTION detect_anomalies(threshold REAL DEFAULT 3.0)
RETURNS TABLE(id BIGINT, pm25 REAL, z_score REAL, timestamp TIMESTAMPTZ) AS $$
BEGIN
  RETURN QUERY
  WITH stats AS (
    SELECT
      AVG(pm25) as mean,
      STDDEV(pm25) as stddev
    FROM air_quality_measurements
    WHERE timestamp >= NOW() - INTERVAL '7 days'
      AND pm25 IS NOT NULL
  )
  SELECT
    m.id,
    m.pm25,
    ABS((m.pm25 - s.mean) / NULLIF(s.stddev, 0)) as z_score,
    m.timestamp
  FROM air_quality_measurements m, stats s
  WHERE ABS((m.pm25 - s.mean) / NULLIF(s.stddev, 0)) > threshold
    AND m.timestamp >= NOW() - INTERVAL '24 hours'
  ORDER BY z_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM detect_anomalies(3.0);
```

### 3. Latest Reading Per Sensor

```sql
CREATE OR REPLACE FUNCTION get_latest_sensor_readings()
RETURNS TABLE(
  sensor_id VARCHAR,
  pm25 REAL,
  temperature REAL,
  timestamp TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT ON (source)
    source as sensor_id,
    air_quality_measurements.pm25,
    0.0 as temperature,  -- Join with weather_data if needed
    air_quality_measurements.timestamp
  FROM air_quality_measurements
  WHERE source LIKE 'sensor_%'
  ORDER BY source, timestamp DESC;
END;
$$ LANGUAGE plpgsql;
```

### 4. Air Quality Index Category

```sql
CREATE OR REPLACE FUNCTION get_aqi_category(pm25_value REAL)
RETURNS TEXT AS $$
BEGIN
  CASE
    WHEN pm25_value <= 12 THEN RETURN 'Good';
    WHEN pm25_value <= 35.4 THEN RETURN 'Moderate';
    WHEN pm25_value <= 55.4 THEN RETURN 'Unhealthy for Sensitive Groups';
    WHEN pm25_value <= 150.4 THEN RETURN 'Unhealthy';
    WHEN pm25_value <= 250.4 THEN RETURN 'Very Unhealthy';
    ELSE RETURN 'Hazardous';
  END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Usage
SELECT pm25, get_aqi_category(pm25) as category
FROM air_quality_measurements
WHERE timestamp >= NOW() - INTERVAL '1 day';
```

## Row Level Security (RLS)

### Enable RLS on Tables

```sql
-- Enable RLS
ALTER TABLE air_quality_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
```

### Public Read Access

```sql
-- Allow anyone to read air quality data
CREATE POLICY "Public read access"
ON air_quality_measurements FOR SELECT
USING (true);

CREATE POLICY "Public read weather"
ON weather_data FOR SELECT
USING (true);

CREATE POLICY "Public read predictions"
ON predictions FOR SELECT
USING (true);
```

### Authenticated Write Access

```sql
-- Only authenticated users can insert measurements
CREATE POLICY "Authenticated write access"
ON air_quality_measurements FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Authenticated insert weather"
ON weather_data FOR INSERT
TO authenticated
WITH CHECK (true);
```

### Admin-Only Access

```sql
-- Only admins can delete measurements
CREATE POLICY "Admin delete only"
ON air_quality_measurements FOR DELETE
TO authenticated
USING (auth.jwt() ->> 'role' = 'admin');

-- Only admins can update sensor metadata
CREATE POLICY "Admin update sensors"
ON sensor_metadata FOR UPDATE
TO authenticated
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

## Common Queries

### Time-Series Queries

```sql
-- Last 24 hours of PM2.5 data
SELECT timestamp, pm25, source
FROM air_quality_measurements
WHERE timestamp >= NOW() - INTERVAL '24 hours'
  AND pm25 IS NOT NULL
ORDER BY timestamp DESC;

-- Hourly average PM2.5 for last 7 days
SELECT
  date_trunc('hour', timestamp) as hour,
  AVG(pm25) as avg_pm25,
  MIN(pm25) as min_pm25,
  MAX(pm25) as max_pm25
FROM air_quality_measurements
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour DESC;
```

### Aggregation Queries

```sql
-- Daily statistics by city
SELECT
  city,
  DATE(timestamp) as date,
  AVG(pm25) as avg_pm25,
  MAX(aqi) as max_aqi,
  COUNT(*) as measurement_count
FROM air_quality_measurements
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY city, DATE(timestamp)
ORDER BY date DESC, city;
```

### Join Queries

```sql
-- Air quality with weather data
SELECT
  aq.timestamp,
  aq.pm25,
  aq.aqi,
  w.temperature,
  w.humidity,
  w.wind_speed
FROM air_quality_measurements aq
LEFT JOIN weather_data w
  ON aq.city = w.city
  AND date_trunc('hour', aq.timestamp) = date_trunc('hour', w.timestamp)
WHERE aq.timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY aq.timestamp DESC;
```

### JSONB Queries

```sql
-- Query by location coordinates
SELECT *
FROM air_quality_measurements
WHERE location @> '{"name": "Paris"}'::jsonb;

-- Extract location coordinates
SELECT
  id,
  location->>'name' as location_name,
  (location->>'lat')::float as latitude,
  (location->>'lon')::float as longitude,
  pm25
FROM air_quality_measurements
WHERE location IS NOT NULL;
```

## Database Migrations

### Creating a Migration

```sql
-- Migration: add_co_pollutant_20251224.sql
BEGIN;

-- Add CO column
ALTER TABLE air_quality_measurements
ADD COLUMN co REAL CHECK (co >= 0);

-- Create index
CREATE INDEX idx_co ON air_quality_measurements(co) WHERE co IS NOT NULL;

-- Add comment
COMMENT ON COLUMN air_quality_measurements.co IS 'Carbon monoxide concentration (μg/m³)';

COMMIT;
```

### Rolling Back

```sql
-- Rollback: remove_co_pollutant_20251224.sql
BEGIN;

DROP INDEX IF EXISTS idx_co;
ALTER TABLE air_quality_measurements DROP COLUMN IF EXISTS co;

COMMIT;
```

## Performance Optimization

### Analyzing Query Performance

```sql
-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM air_quality_measurements
WHERE city = 'paris'
  AND timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC
LIMIT 100;
```

### Vacuum and Analyze

```sql
-- Reclaim storage and update statistics
VACUUM ANALYZE air_quality_measurements;
VACUUM ANALYZE weather_data;
```

### Partitioning (for large datasets)

```sql
-- Create partitioned table by month
CREATE TABLE air_quality_measurements_partitioned (
  LIKE air_quality_measurements INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE air_quality_2025_01 PARTITION OF air_quality_measurements_partitioned
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE air_quality_2025_02 PARTITION OF air_quality_measurements_partitioned
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

## Best Practices

### Schema Design
- Use appropriate data types (REAL for floats, INTEGER for whole numbers)
- Add CHECK constraints for data validation
- Use TIMESTAMPTZ for all timestamps
- Add meaningful comments to tables and columns

### Indexing
- Index columns used in WHERE clauses
- Create composite indexes for frequently combined filters
- Use GIN indexes for JSONB columns
- Monitor index usage with pg_stat_user_indexes

### Security
- Enable RLS on all tables
- Use service role key only in backend
- Never expose service key to frontend
- Audit policies regularly

### Performance
- Use LIMIT on unbounded queries
- Aggregate data for reporting
- Archive old data periodically
- Monitor query performance

## References
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Supabase SQL: https://supabase.com/docs/guides/database
- PostGIS (for geospatial): https://postgis.net/

## Trade-offs

**JSONB vs. Separate Columns:**
- JSONB: Flexible schema, slower queries
- Columns: Faster, enforced types, requires migrations

**Indexes:**
- More indexes = faster reads, slower writes
- Balance based on query patterns

**RLS:**
- Security at database level
- May impact query performance
- Test with realistic data volumes
