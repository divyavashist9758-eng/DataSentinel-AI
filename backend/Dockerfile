FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for scientific libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY sample_data/ ./sample_data/
COPY run.py .

# Create storage and upload directories
RUN mkdir -p /app/storage/uploads /app/storage/remediated /app/storage/exports

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    STORAGE_DIR=/app/storage

EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/auth/health || exit 1

CMD ["python", "run.py"]

