-- ============================================================================
-- TABLES MANQUANTES POUR SMART CITY PLATFORM
-- A exécuter dans Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- Table: predictions
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  city VARCHAR(100) NOT NULL,
  pollutant VARCHAR(20) NOT NULL DEFAULT 'PM2.5',
  predicted_value REAL NOT NULL CHECK (predicted_value >= 0),
  confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 1),

  -- JSON fields
  prediction_range JSONB,  -- {lower: number, upper: number}
  aqi_level JSONB,         -- {name: string, color: string, description: string}
  model_metrics JSONB,     -- {r2: number, mape: number, rmse: number}

  -- Timestamps
  prediction_for TIMESTAMPTZ NOT NULL,
  predicted_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT unique_prediction_per_day UNIQUE (city, pollutant, prediction_for)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_city_date ON predictions(city, prediction_for DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_for DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_pollutant ON predictions(pollutant);

-- RLS Policies
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public read predictions" ON predictions;
CREATE POLICY "Public read predictions" ON predictions FOR SELECT USING (true);

DROP POLICY IF EXISTS "Authenticated write predictions" ON predictions;
CREATE POLICY "Authenticated write predictions" ON predictions FOR INSERT TO authenticated WITH CHECK (true);

COMMENT ON TABLE predictions IS 'ML predictions for air quality (PM2.5, PM10, etc.)';


-- ============================================================================
-- Table: alerts
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
  id BIGSERIAL PRIMARY KEY,
  alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('threshold_exceeded', 'anomaly_detected', 'sensor_offline')),
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),

  -- Alert details
  city VARCHAR(100),
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_city ON alerts(city, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);

-- RLS Policies
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public read alerts" ON alerts;
CREATE POLICY "Public read alerts" ON alerts FOR SELECT USING (true);

DROP POLICY IF EXISTS "Authenticated write alerts" ON alerts;
CREATE POLICY "Authenticated write alerts" ON alerts FOR INSERT TO authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated update alerts" ON alerts;
CREATE POLICY "Authenticated update alerts" ON alerts FOR UPDATE TO authenticated USING (true);

COMMENT ON TABLE alerts IS 'System alerts for pollution events and sensor issues';


-- ============================================================================
-- END OF MIGRATIONS
-- ============================================================================

-- Verification queries
SELECT 'predictions' as table_name, COUNT(*) as row_count FROM predictions
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts;
