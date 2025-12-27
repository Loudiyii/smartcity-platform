"""
Create alerts table in Supabase
Run this script once to set up the alerts table for anomaly detection
"""

from app.config import get_supabase_client

def create_alerts_table():
    """Create the alerts table with all necessary columns."""

    supabase = get_supabase_client()

    # SQL to create alerts table with all necessary columns
    sql = """
    -- Create alerts table
    CREATE TABLE IF NOT EXISTS alerts (
      id BIGSERIAL PRIMARY KEY,

      -- Alert classification
      alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('threshold_exceeded', 'anomaly_detected', 'sensor_offline')),
      severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),

      -- Location
      city VARCHAR(100),

      -- Alert details
      pollutant VARCHAR(20),
      value REAL,
      threshold REAL,
      message TEXT,

      -- Additional data (JSONB for flexible storage)
      data JSONB,

      -- Status
      is_active BOOLEAN DEFAULT TRUE,
      sent_at TIMESTAMPTZ,
      acknowledged BOOLEAN DEFAULT FALSE,
      acknowledged_at TIMESTAMPTZ,

      -- Timestamps
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_alerts_city ON alerts(city, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type, is_active);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active, created_at DESC);

    -- Enable RLS (Row Level Security)
    ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

    -- Create policy to allow all operations for authenticated users
    DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON alerts;
    CREATE POLICY "Allow all operations for authenticated users"
      ON alerts
      FOR ALL
      USING (true)
      WITH CHECK (true);

    -- Create policy for anonymous read access
    DROP POLICY IF EXISTS "Allow anonymous read access" ON alerts;
    CREATE POLICY "Allow anonymous read access"
      ON alerts
      FOR SELECT
      USING (true);

    COMMENT ON TABLE alerts IS 'System alerts for pollution events and anomalies';
    """

    try:
        # Execute using Supabase RPC or direct SQL
        # Note: Supabase Python client doesn't directly support DDL
        # We'll need to execute this via psycopg2 or Supabase SQL Editor

        print("=" * 70)
        print("ALERTS TABLE CREATION SQL")
        print("=" * 70)
        print("\nPlease execute the following SQL in your Supabase SQL Editor:")
        print("(Dashboard > SQL Editor > New Query > Paste and Run)\n")
        print(sql)
        print("\n" + "=" * 70)
        print("\nOR use the direct database connection method below...")

        # Alternative: Direct PostgreSQL connection
        from app.config import get_settings
        settings = get_settings()

        print("\n" + "=" * 70)
        print("ALTERNATIVE: Using psycopg2 (if available)")
        print("=" * 70)

        try:
            import psycopg2

            # Extract database connection string
            # Supabase connection string format: postgresql://postgres:[password]@[host]:5432/postgres
            db_url = settings.SUPABASE_URL.replace('https://', '')
            project_ref = db_url.split('.')[0]

            print(f"\nProject: {project_ref}")
            print("\nTo connect, you need your database password (not the API key)")
            print("Find it in: Supabase Dashboard > Settings > Database > Connection string")

            # Prompt for connection (optional)
            print("\n[INFO] psycopg2 available but requires manual database password")
            print("[INFO] Use Supabase SQL Editor for easiest setup")

        except ImportError:
            print("\n[INFO] psycopg2 not installed")
            print("[INFO] Use Supabase SQL Editor to execute the SQL above")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


if __name__ == "__main__":
    print("\n[SETUP] Smart City - Alerts Table Setup\n")
    create_alerts_table()
