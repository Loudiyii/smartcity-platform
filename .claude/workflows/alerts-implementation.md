# Workflow: Alerts Implementation

## Objectif
Système d'alertes automatiques avec notifications email.

## Référence
- **User Stories:** US-015, US-016
- **Skills:** `backend-api`, `database-schema`

## Étapes

### 1. Alert Service
```python
# backend/app/services/alert_service.py
class AlertService:
    def check_thresholds(self, pm25: float):
        if pm25 > 50:
            self.create_alert('high_pm25', pm25)
            self.send_email_notification()
```

### 2. Email Notification
```python
import smtplib

def send_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.send_message(msg)
```

### 3. Scheduled Checks
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(check_alerts, 'interval', minutes=15)
```

## Critères
- [ ] Alerts créées automatiquement
- [ ] Email envoyé
- [ ] UI affiche alertes
