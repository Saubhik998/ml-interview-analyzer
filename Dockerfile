# Use latest slim Python image
FROM python:3.11-slim

# --- System Setup ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies for building packages (for example, gcc)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# --- Python Setup ---
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- App Code ---
COPY ./app ./app

# --- Port Exposure (Matches Compose) ---
EXPOSE 8081

# --- Default Run Command (with explicit port) ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
