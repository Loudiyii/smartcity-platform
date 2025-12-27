"""
Analytics API Endpoints
Provides correlation analysis and statistical insights
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
import pandas as pd

from app.config import get_supabase_client

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/correlation")
async def get_correlation_data(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=30, description="Days of data to analyze"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get time-aligned pollution and weather data for correlation analysis.

    Returns synchronized time-series data for:
    - PM2.5, PM10, NO2, O3 (pollution)
    - Temperature, Humidity, Wind Speed, Pressure (weather)

    **Use case:** Dual-axis charts showing pollution-weather correlations
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Fetch air quality data
        aq_data = []
        offset = 0
        batch_size = 1000

        while True:
            aq_response = supabase.table('air_quality_measurements')\
                .select('timestamp, pm25, pm10, no2, o3, aqi')\
                .eq('city', city)\
                .gte('timestamp', start_date.isoformat())\
                .lte('timestamp', end_date.isoformat())\
                .order('timestamp')\
                .range(offset, offset + batch_size - 1)\
                .execute()

            if not aq_response.data:
                break

            aq_data.extend(aq_response.data)

            if len(aq_response.data) < batch_size:
                break

            offset += batch_size

        # Fetch weather data
        weather_data = []
        offset = 0

        while True:
            weather_response = supabase.table('weather_data')\
                .select('timestamp, temperature, humidity, pressure, wind_speed')\
                .eq('city', city)\
                .gte('timestamp', start_date.isoformat())\
                .lte('timestamp', end_date.isoformat())\
                .order('timestamp')\
                .range(offset, offset + batch_size - 1)\
                .execute()

            if not weather_response.data:
                break

            weather_data.extend(weather_response.data)

            if len(weather_response.data) < batch_size:
                break

            offset += batch_size

        if not aq_data or not weather_data:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for {city}"
            )

        # Convert to DataFrames
        aq_df = pd.DataFrame(aq_data)
        weather_df = pd.DataFrame(weather_data)

        # Parse timestamps
        aq_df['timestamp'] = pd.to_datetime(aq_df['timestamp'])
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

        # Merge on timestamp
        merged_df = pd.merge(
            aq_df,
            weather_df,
            on='timestamp',
            how='inner'
        )

        # Sort by timestamp
        merged_df = merged_df.sort_values('timestamp')

        # Convert to lists for JSON response
        result = {
            'city': city,
            'days': days,
            'data_points': len(merged_df),
            'timestamps': [ts.isoformat() for ts in merged_df['timestamp'].tolist()],
            'pollution': {
                'pm25': merged_df['pm25'].tolist(),
                'pm10': merged_df['pm10'].tolist(),
                'no2': merged_df['no2'].tolist(),
                'o3': merged_df['o3'].tolist(),
                'aqi': merged_df['aqi'].tolist()
            },
            'weather': {
                'temperature': merged_df['temperature'].tolist(),
                'humidity': merged_df['humidity'].tolist(),
                'pressure': merged_df['pressure'].tolist(),
                'wind_speed': merged_df['wind_speed'].tolist()
            }
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Correlation analysis failed: {str(e)}"
        )


@router.get("/correlation/stats")
async def get_correlation_statistics(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=30, description="Days of data"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Calculate correlation coefficients between pollution and weather variables.

    Returns Pearson correlation coefficients showing:
    - PM2.5 vs Temperature, Humidity, Wind Speed, Pressure
    - PM10 vs Weather variables
    - NO2 vs Weather variables

    **Interpretation:**
    - 1.0: Perfect positive correlation
    - 0.0: No correlation
    - -1.0: Perfect negative correlation
    """
    try:
        # Get correlation data
        data = await get_correlation_data(city, days, supabase)

        # Convert to DataFrame for correlation calculation
        df_dict = {
            'pm25': data['pollution']['pm25'],
            'pm10': data['pollution']['pm10'],
            'no2': data['pollution']['no2'],
            'o3': data['pollution']['o3'],
            'temperature': data['weather']['temperature'],
            'humidity': data['weather']['humidity'],
            'pressure': data['weather']['pressure'],
            'wind_speed': data['weather']['wind_speed']
        }

        df = pd.DataFrame(df_dict)

        # Calculate correlation matrix
        corr_matrix = df.corr()

        # Extract key correlations
        correlations = {
            'pm25_vs_weather': {
                'temperature': float(corr_matrix.loc['pm25', 'temperature']),
                'humidity': float(corr_matrix.loc['pm25', 'humidity']),
                'pressure': float(corr_matrix.loc['pm25', 'pressure']),
                'wind_speed': float(corr_matrix.loc['pm25', 'wind_speed'])
            },
            'pm10_vs_weather': {
                'temperature': float(corr_matrix.loc['pm10', 'temperature']),
                'humidity': float(corr_matrix.loc['pm10', 'humidity']),
                'pressure': float(corr_matrix.loc['pm10', 'pressure']),
                'wind_speed': float(corr_matrix.loc['pm10', 'wind_speed'])
            },
            'no2_vs_weather': {
                'temperature': float(corr_matrix.loc['no2', 'temperature']),
                'humidity': float(corr_matrix.loc['no2', 'humidity']),
                'pressure': float(corr_matrix.loc['no2', 'pressure']),
                'wind_speed': float(corr_matrix.loc['no2', 'wind_speed'])
            }
        }

        return {
            'city': city,
            'days_analyzed': days,
            'correlations': correlations,
            'data_points': len(df)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Correlation statistics failed: {str(e)}"
        )
