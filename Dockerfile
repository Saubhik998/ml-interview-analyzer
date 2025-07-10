# Use official Python 3.11 base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies (optional but recommended)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv or upgrade pip if needed (optional)
RUN python -m pip install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Set environment variable for unbuffered logs
ENV PYTHONUNBUFFERED=1

# Default command to run the app with hot reload support in development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
