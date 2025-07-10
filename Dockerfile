# Use official Python 3.11 base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Set environment variable for unbuffered logs
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in CI/CD or docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
