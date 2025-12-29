# Dockerfile for Smart City Backend
# Handles monorepo structure for Railway deployment

FROM python:3.11-slim

WORKDIR /code

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app /code/app

# Start command - Railway provides $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
