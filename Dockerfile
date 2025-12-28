# Dockerfile for Smart City Backend
# Handles monorepo structure for Railway deployment

FROM python:3.11-slim

WORKDIR /app

# Copy backend directory
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app

# Expose port
EXPOSE 8080

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
