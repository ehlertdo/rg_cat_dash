# Use a small Python base
FROM python:3.13-slim

# Install OS dependencies (optional, e.g., for fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining files
COPY . .

# Set environment variables for better behavior inside containers
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Force stdout/stderr to be unbuffered
ENV PYTHONUNBUFFERED=1

# Expose the port Koyeb expects (default 8080)
EXPOSE 8080

# Run via gunicorn (recommended for production)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
