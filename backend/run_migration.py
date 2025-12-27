"""
Database Migration: Create Alerts Table
Executes SQL to create the alerts table in Supabase PostgreSQL
"""

import psycopg2
from app.config import get_settings

def run_migration():
    """Execute the alerts table creation SQL."""

    settings = get_settings()

    # Construct PostgreSQL connection string
    # Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

    # Extract project reference from Supabase URL
    supabase_url = settings.SUPABASE_URL
    project_ref = supabase_url.replace('https://', '').split('.')[0]

    print(f"\n[INFO] Project Reference: {project_ref}")
    print(f"[INFO] Supabase URL: {supabase_url}")

    # Database connection string (requires database password, not API key)
    # User needs to provide their database password from Supabase Dashboard
    print("\n" + "=" * 70)
    print("DATABASE CONNECTION REQUIRED")
    print("=" * 70)
    print("\nTo run this migration, you need your Supabase database password:")
    print("1. Go to: https://supabase.com/dashboard/project/" + project_ref)
    print("2. Navigate to: Settings > Database")
    print("3. Under 'Connection string', find 'Connection pooling'")
    print("4. Copy the password from the connection string")
    print("\n" + "=" * 70)

    # Prompt for password
    import getpass
    db_password = getpass.getpass("\nEnter your Supabase database password: ")

    if not db_password or db_password.strip() == "":
        print("\n[ERROR] No password provided. Exiting.")
        return False

    # Connection string for connection pooling (port 6543)
    conn_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    # SQL to create alerts table
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

    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON alerts;
    DROP POLICY IF EXISTS "Allow anonymous read access" ON alerts;

    -- Create policy to allow all operations for authenticated users
    CREATE POLICY "Allow all operations for authenticated users"
      ON alerts
      FOR ALL
      USING (true)
      WITH CHECK (true);

    -- Create policy for anonymous read access
    CREATE POLICY "Allow anonymous read access"
      ON alerts
      FOR SELECT
      USING (true);

    -- Add table comment
    COMMENT ON TABLE alerts IS 'System alerts for pollution events and anomalies';
    """

    try:
        print("\n[INFO] Connecting to database...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("[INFO] Executing migration SQL...")
        cursor.execute(sql)

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("[SUCCESS] Alerts table created successfully!")
        print("=" * 70)
        print("\nYou can now use the anomaly detection features.")
        print("The dashboard will display detected anomalies automatically.\n")

        return True

    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your database password is correct")
        print("2. Check that your IP is allowed in Supabase Dashboard > Settings > Database > Connection Pooling")
        print("3. Ensure you're using the connection pooling port (6543)")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("\n[MIGRATION] Smart City - Create Alerts Table\n")
    success = run_migration()

    if not success:
        print("\n[ALTERNATIVE] You can also execute the SQL manually:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Create new query")
        print("3. Copy the SQL from create_alerts_table.py output")
        print("4. Run the query")
