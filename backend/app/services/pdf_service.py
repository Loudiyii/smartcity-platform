"""
PDF Report Generation Service
Creates downloadable PDF reports with air quality charts and statistics
"""

import io
from datetime import datetime, timedelta
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from supabase import Client


class PDFReportService:
    """Generates PDF reports with air quality data and visualizations."""

    def __init__(self, supabase_client: Client):
        """
        Initialize PDF report service.

        Args:
            supabase_client: Supabase client for data access
        """
        self.supabase = supabase_client
        self.styles = getSampleStyleSheet()

    async def generate_report(
        self,
        city: str,
        start_date: datetime,
        end_date: datetime
    ) -> bytes:
        """
        Generate PDF report for a city and date range.

        Args:
            city: City name
            start_date: Report start date
            end_date: Report end date

        Returns:
            PDF file as bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Build report elements
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f"Rapport Qualité de l'Air - {city}", title_style))

        # Subtitle with date range
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        date_range = f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(date_range, subtitle_style))

        elements.append(Spacer(1, 0.3*inch))

        # Fetch data
        data = await self._fetch_data(city, start_date, end_date)

        if not data:
            elements.append(Paragraph("Aucune donnée disponible pour cette période", self.styles['Normal']))
        else:
            # Statistics table
            stats_table = self._create_statistics_table(data)
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))

            # Generate charts
            pm25_chart = self._create_pm25_chart(data)
            if pm25_chart:
                elements.append(Paragraph("Évolution PM2.5", self.styles['Heading2']))
                elements.append(Spacer(1, 0.1*inch))
                elements.append(pm25_chart)
                elements.append(Spacer(1, 0.3*inch))

            # Page break before weather chart
            elements.append(PageBreak())

            weather_chart = self._create_weather_chart(data)
            if weather_chart:
                elements.append(Paragraph("Conditions Météorologiques", self.styles['Heading2']))
                elements.append(Spacer(1, 0.1*inch))
                elements.append(weather_chart)

        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER
        )
        footer_text = f"Smart City Platform - Généré le {datetime.utcnow().strftime('%d/%m/%Y à %H:%M')}"
        elements.append(Paragraph(footer_text, footer_style))

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    async def _fetch_data(self, city: str, start_date: datetime, end_date: datetime):
        """Fetch air quality and weather data."""
        # Fetch air quality
        aq_data = []
        offset = 0
        batch_size = 1000

        while True:
            aq_response = self.supabase.table('air_quality_measurements')\
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

        # Fetch weather
        weather_data = []
        offset = 0

        while True:
            weather_response = self.supabase.table('weather_data')\
                .select('timestamp, temperature, humidity, wind_speed')\
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

        return {'air_quality': aq_data, 'weather': weather_data}

    def _create_statistics_table(self, data):
        """Create statistics summary table."""
        aq_data = data['air_quality']

        if not aq_data:
            return Paragraph("Pas de données", self.styles['Normal'])

        # Calculate stats
        pm25_values = [d['pm25'] for d in aq_data]
        pm10_values = [d['pm10'] for d in aq_data]
        no2_values = [d['no2'] for d in aq_data]

        table_data = [
            ['Statistique', 'PM2.5 (μg/m³)', 'PM10 (μg/m³)', 'NO2 (μg/m³)'],
            ['Moyenne', f"{sum(pm25_values)/len(pm25_values):.1f}",
             f"{sum(pm10_values)/len(pm10_values):.1f}",
             f"{sum(no2_values)/len(no2_values):.1f}"],
            ['Maximum', f"{max(pm25_values):.1f}",
             f"{max(pm10_values):.1f}",
             f"{max(no2_values):.1f}"],
            ['Minimum', f"{min(pm25_values):.1f}",
             f"{min(pm10_values):.1f}",
             f"{min(no2_values):.1f}"]
        ]

        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        return table

    def _create_pm25_chart(self, data):
        """Create PM2.5 time series chart."""
        aq_data = data['air_quality']

        if not aq_data:
            return None

        timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in aq_data]
        pm25_values = [d['pm25'] for d in aq_data]

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(timestamps, pm25_values, color='#ef4444', linewidth=2)
        ax.fill_between(timestamps, pm25_values, alpha=0.2, color='#ef4444')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('PM2.5 (μg/m³)', fontsize=10)
        ax.set_title('Évolution de la concentration PM2.5', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=6*inch, height=3.5*inch)

    def _create_weather_chart(self, data):
        """Create weather conditions chart."""
        weather_data = data['weather']

        if not weather_data:
            return None

        timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in weather_data]
        temps = [d['temperature'] for d in weather_data]
        humidity = [d['humidity'] for d in weather_data]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5))

        # Temperature
        ax1.plot(timestamps, temps, color='#f59e0b', linewidth=2)
        ax1.set_ylabel('Température (°C)', fontsize=10)
        ax1.set_title('Température', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

        # Humidity
        ax2.plot(timestamps, humidity, color='#3b82f6', linewidth=2)
        ax2.set_xlabel('Date', fontsize=10)
        ax2.set_ylabel('Humidité (%)', fontsize=10)
        ax2.set_title('Humidité', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=6*inch, height=4.5*inch)
