"""
Anomaly Detection for Air Quality Measurements
Detects abnormal sensor readings using Z-score and Isolation Forest
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from supabase import Client


class AnomalyDetector:
    """Detects anomalies in air quality measurements."""

    def __init__(self, supabase_client: Client):
        """
        Initialize anomaly detector.

        Args:
            supabase_client: Supabase client for database access
        """
        self.supabase = supabase_client
        self.z_threshold = 3.0  # Standard deviations for Z-score
        self.isolation_forest = None

    async def detect_zscore_anomalies(
        self,
        city: str,
        lookback_days: int = 7,
        threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Z-score method.

        Z-score = (value - mean) / std_dev
        Anomaly if |Z-score| > threshold (default 3.0)

        Args:
            city: City name
            lookback_days: Days of historical data for baseline
            threshold: Z-score threshold for anomaly

        Returns:
            List of anomaly records
        """
        # Fetch recent data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        response = self.supabase.table('air_quality_measurements')\
            .select('*')\
            .eq('city', city)\
            .gte('timestamp', start_date.isoformat())\
            .lte('timestamp', end_date.isoformat())\
            .order('timestamp')\
            .range(0, 10000)\
            .execute()

        if not response.data or len(response.data) < 24:
            return []

        df = pd.DataFrame(response.data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calculate statistics for PM2.5
        mean_pm25 = df['pm25'].mean()
        std_pm25 = df['pm25'].std()

        if std_pm25 == 0:
            return []  # No variation, no anomalies

        # Calculate Z-scores
        df['z_score'] = (df['pm25'] - mean_pm25) / std_pm25
        df['is_anomaly'] = df['z_score'].abs() > threshold

        # Filter anomalies
        anomalies_df = df[df['is_anomaly']]

        anomalies = []
        for _, row in anomalies_df.iterrows():
            anomalies.append({
                'city': city,
                'timestamp': row['timestamp'].isoformat(),
                'pm25': float(row['pm25']),
                'expected_pm25': float(mean_pm25),
                'z_score': float(row['z_score']),
                'detection_method': 'z_score',
                'severity': self._calculate_severity(abs(row['z_score']), threshold),
                'detected_at': datetime.utcnow().isoformat()
            })

        return anomalies

    async def detect_isolation_forest_anomalies(
        self,
        city: str,
        lookback_days: int = 7,
        contamination: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Isolation Forest.

        Isolation Forest detects outliers by isolating instances.
        Anomalies are easier to isolate than normal points.

        Args:
            city: City name
            lookback_days: Days of historical data for training
            contamination: Expected proportion of outliers (0.1 = 10%)

        Returns:
            List of anomaly records
        """
        # Fetch recent data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        response = self.supabase.table('air_quality_measurements')\
            .select('*')\
            .eq('city', city)\
            .gte('timestamp', start_date.isoformat())\
            .lte('timestamp', end_date.isoformat())\
            .order('timestamp')\
            .range(0, 10000)\
            .execute()

        if not response.data or len(response.data) < 100:
            return []  # Need minimum data for Isolation Forest

        df = pd.DataFrame(response.data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Features for anomaly detection
        feature_cols = ['pm25', 'pm10', 'no2', 'o3']
        X = df[feature_cols].values

        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        predictions = iso_forest.fit_predict(X)

        # -1 indicates anomaly, 1 indicates normal
        df['is_anomaly'] = predictions == -1
        df['anomaly_score'] = iso_forest.score_samples(X)

        # Filter anomalies
        anomalies_df = df[df['is_anomaly']]

        anomalies = []
        for _, row in anomalies_df.iterrows():
            anomalies.append({
                'city': city,
                'timestamp': row['timestamp'].isoformat(),
                'pm25': float(row['pm25']),
                'pm10': float(row['pm10']),
                'no2': float(row['no2']),
                'o3': float(row['o3']),
                'anomaly_score': float(row['anomaly_score']),
                'detection_method': 'isolation_forest',
                'severity': self._calculate_if_severity(row['anomaly_score']),
                'detected_at': datetime.utcnow().isoformat()
            })

        return anomalies

    async def detect_all_anomalies(
        self,
        city: str,
        lookback_days: int = 7
    ) -> Dict[str, Any]:
        """
        Run both detection methods and combine results.

        Args:
            city: City name
            lookback_days: Days of historical data

        Returns:
            Dictionary with anomalies from both methods
        """
        zscore_anomalies = await self.detect_zscore_anomalies(city, lookback_days)
        iforest_anomalies = await self.detect_isolation_forest_anomalies(city, lookback_days)

        # Deduplicate by timestamp (if same time detected by both methods)
        all_anomalies = []
        timestamps_seen = set()

        for anomaly in zscore_anomalies + iforest_anomalies:
            ts = anomaly['timestamp']
            if ts not in timestamps_seen:
                all_anomalies.append(anomaly)
                timestamps_seen.add(ts)

        return {
            'city': city,
            'total_anomalies': len(all_anomalies),
            'zscore_count': len(zscore_anomalies),
            'isolation_forest_count': len(iforest_anomalies),
            'anomalies': sorted(all_anomalies, key=lambda x: x['timestamp'], reverse=True),
            'lookback_days': lookback_days,
            'detected_at': datetime.utcnow().isoformat()
        }

    async def save_anomaly_to_alerts(self, anomaly: Dict[str, Any]) -> None:
        """
        Save detected anomaly to alerts table.

        Args:
            anomaly: Anomaly record
        """
        alert_record = {
            'city': anomaly['city'],
            'alert_type': 'anomaly_detected',
            'severity': anomaly['severity'],
            'message': f"Anomaly detected: PM2.5 = {anomaly['pm25']:.1f} ug/m3",
            'data': anomaly,
            'is_active': True,
            'created_at': anomaly['detected_at']
        }

        self.supabase.table('alerts').insert(alert_record).execute()

    @staticmethod
    def _calculate_severity(z_score_abs: float, threshold: float) -> str:
        """
        Calculate severity based on Z-score magnitude.

        Args:
            z_score_abs: Absolute value of Z-score
            threshold: Base threshold

        Returns:
            Severity level (low, medium, high, critical)
        """
        if z_score_abs < threshold:
            return 'low'
        elif z_score_abs < threshold * 1.5:
            return 'medium'
        elif z_score_abs < threshold * 2:
            return 'high'
        else:
            return 'critical'

    @staticmethod
    def _calculate_if_severity(anomaly_score: float) -> str:
        """
        Calculate severity based on Isolation Forest anomaly score.

        Lower (more negative) scores indicate stronger anomalies.

        Args:
            anomaly_score: Isolation Forest anomaly score

        Returns:
            Severity level
        """
        if anomaly_score > -0.1:
            return 'low'
        elif anomaly_score > -0.2:
            return 'medium'
        elif anomaly_score > -0.3:
            return 'high'
        else:
            return 'critical'

    async def get_recent_anomalies(
        self,
        city: Optional[str] = None,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent anomalies from alerts table.

        Args:
            city: City name (optional, None for all cities)
            hours: Hours to look back
            limit: Maximum number of results

        Returns:
            List of recent anomaly alerts
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)

        query = self.supabase.table('alerts')\
            .select('*')\
            .eq('alert_type', 'anomaly_detected')\
            .gte('created_at', start_time.isoformat())\
            .order('created_at', desc=True)\
            .limit(limit)

        if city:
            query = query.eq('city', city)

        response = query.execute()

        return response.data
