-- Smart City Platform - Database Schema
-- Phase 1 MVP - Sprint 1
-- PostgreSQL 17 (Supabase)

-- ============================================================================
-- Table 1: air_quality_measurements
-- ============================================================================

CREATE TABLE IF NOT EXISTS air_quality_measurements (
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
CREATE INDEX IF NOT EXISTS idx_timestamp_source ON air_quality_measurements(timestamp DESC, source);
CREATE INDEX IF NOT EXISTS idx_city_timestamp ON air_quality_measurements(city, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_source ON air_quality_measurements(source);
CREATE INDEX IF NOT EXISTS idx_location ON air_quality_measurements USING GIN (location);

-- Comments
COMMENT ON TABLE air_quality_measurements IS 'Time-series air quality data from APIs and IoT sensors';
COMMENT ON COLUMN air_quality_measurements.source IS 'Data source: api or sensor_xxx';


-- ============================================================================
-- Table 2: weather_data
-- ============================================================================

CREATE TABLE IF NOT EXISTS weather_data (
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

CREATE INDEX IF NOT EXISTS idx_weather_city_timestamp ON weather_data(city, timestamp DESC);

COMMENT ON TABLE weather_data IS 'Weather data from OpenWeatherMap API';


-- ============================================================================
-- Table 3: sensor_metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_metadata (
  sensor_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  location JSONB NOT NULL,               -- {lat, lon, address}
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'offline')),
  last_reading_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sensor_location ON sensor_metadata USING GIN (location);
CREATE INDEX IF NOT EXISTS idx_sensor_status ON sensor_metadata(status);

COMMENT ON TABLE sensor_metadata IS 'IoT sensor registry and status';


-- ============================================================================
-- Table 4: predictions (for Phase 2, structure ready)
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  pollutant VARCHAR(20) NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_for_date DESC);

COMMENT ON TABLE predictions IS 'ML predictions for air quality';


-- ============================================================================
-- Table 5: alerts (for Phase 2, structure ready)
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
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

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, created_at DESC);

COMMENT ON TABLE alerts IS 'System alerts for pollution events';


-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS
ALTER TABLE air_quality_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Public read access for all tables
CREATE POLICY "Public read air quality" ON air_quality_measurements FOR SELECT USING (true);
CREATE POLICY "Public read weather" ON weather_data FOR SELECT USING (true);
CREATE POLICY "Public read sensors" ON sensor_metadata FOR SELECT USING (true);
CREATE POLICY "Public read predictions" ON predictions FOR SELECT USING (true);
CREATE POLICY "Public read alerts" ON alerts FOR SELECT USING (true);

-- Authenticated write access
CREATE POLICY "Authenticated write air quality" ON air_quality_measurements FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Authenticated write weather" ON weather_data FOR INSERT TO authenticated WITH CHECK (true);


-- ============================================================================
-- Utility Functions
-- ============================================================================

-- Function: Get average PM2.5 over last N hours
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


-- ============================================================================
-- Initial Data - Sensor Metadata (3 sensors)
-- ============================================================================

INSERT INTO sensor_metadata (sensor_id, name, location, status) VALUES
  ('sensor_001', 'Paris Centre', '{"lat": 48.8566, "lon": 2.3522, "address": "Paris Centre"}'::jsonb, 'active'),
  ('sensor_002', 'Paris Nord', '{"lat": 48.8738, "lon": 2.2950, "address": "Paris Nord"}'::jsonb, 'active'),
  ('sensor_003', 'Paris Sud', '{"lat": 48.8414, "lon": 2.3209, "address": "Paris Sud"}'::jsonb, 'active')
ON CONFLICT (sensor_id) DO NOTHING;


-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
