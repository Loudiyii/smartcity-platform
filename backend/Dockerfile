# Backend Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Copy entire backend directory content to /app
COPY backend/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Railway provides PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
