"""
Email Service for Sending Alert Notifications
Sends email alerts via SMTP when air quality thresholds are exceeded
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime

from app.config import get_settings

settings = get_settings()


class EmailService:
    """Handles email notifications for alerts."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else 'smtp.gmail.com'
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587
        self.smtp_user = settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else None
        self.smtp_password = settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else None
        self.enabled = bool(self.smtp_user and self.smtp_password)

    def send_alert_email(
        self,
        to_emails: List[str],
        city: str,
        pm25: float,
        threshold: float,
        recommendations: List[str],
        severity: str
    ) -> bool:
        """
        Send air quality alert email.

        Args:
            to_emails: List of recipient email addresses
            city: City name
            pm25: Current PM2.5 level
            threshold: Threshold exceeded
            recommendations: List of health recommendations
            severity: Alert severity

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("[Email] SMTP not configured, skipping email send")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Alerte Qualité de l'Air - {city}"
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(to_emails)

            # Create HTML body
            html_body = self._create_html_body(
                city, pm25, threshold, recommendations, severity
            )

            # Create plain text fallback
            text_body = self._create_text_body(
                city, pm25, threshold, recommendations
            )

            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"[Email] Alert email sent to {len(to_emails)} recipients")
            return True

        except Exception as e:
            print(f"[Email] Failed to send email: {e}")
            return False

    def _create_html_body(
        self,
        city: str,
        pm25: float,
        threshold: float,
        recommendations: List[str],
        severity: str
    ) -> str:
        """Create HTML email body."""
        severity_colors = {
            'low': '#3b82f6',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'critical': '#991b1b'
        }
        color = severity_colors.get(severity, '#f59e0b')

        recs_html = ''.join([f'<li style="margin-bottom: 8px;">{rec}</li>' for rec in recommendations])

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Alerte Qualité de l'Air</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">{city} - {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}</p>
            </div>

            <div style="background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb;">
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: {color};">Seuil PM2.5 Dépassé</h2>
                    <div style="font-size: 48px; font-weight: bold; color: {color}; margin: 15px 0;">
                        {pm25:.1f} <span style="font-size: 24px; color: #666;">μg/m³</span>
                    </div>
                    <p style="margin: 10px 0; color: #666;">
                        Seuil: {threshold:.1f} μg/m³ | Niveau: <strong>{severity.upper()}</strong>
                    </p>
                </div>

                <div style="background-color: white; padding: 20px; border-radius: 8px;">
                    <h3 style="margin: 0 0 15px 0; color: #111;">Recommandations</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #444;">
                        {recs_html}
                    </ul>
                </div>
            </div>

            <div style="background-color: #f3f4f6; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                <p style="margin: 0;">
                    Smart City Platform - Surveillance Qualité de l'Air<br>
                    Cet email a été généré automatiquement
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def _create_text_body(
        self,
        city: str,
        pm25: float,
        threshold: float,
        recommendations: List[str]
    ) -> str:
        """Create plain text email body."""
        recs_text = '\n'.join([f'- {rec}' for rec in recommendations])

        text = f"""
ALERTE QUALITÉ DE L'AIR - {city}
{datetime.utcnow().strftime('%d/%m/%Y %H:%M')}

SEUIL PM2.5 DÉPASSÉ
Niveau actuel: {pm25:.1f} μg/m³
Seuil: {threshold:.1f} μg/m³

RECOMMANDATIONS:
{recs_text}

---
Smart City Platform - Surveillance Qualité de l'Air
Cet email a été généré automatiquement.
        """
        return text
