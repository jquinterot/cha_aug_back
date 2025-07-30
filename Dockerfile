# Stage 1: Build stage
FROM python:3.12-slim as builder

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libopenblas-dev \
    libgfortran5 \
    libstdc++6 \
    g++ \
    gcc \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy only the necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/requirements.txt .
COPY . .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    MODEL_TYPE=local

# Create necessary directories
RUN mkdir -p /app/vector_store

# Expose the port the app runs on
EXPOSE $PORT

# Install gunicorn and uvicorn in the runtime stage
RUN pip install --no-cache-dir gunicorn uvicorn[standard]

# Ensure the directory for the socket exists
RUN mkdir -p /var/run/gunicorn

# Create a non-root user to run the application
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Use a shell form of CMD to ensure environment variables are properly expanded
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120", "app.main:app"]
