# Backend Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies from backend directory
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from backend directory
COPY backend/app ./app

# Railway provides PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
