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

# Install system dependencies needed for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY --chown=www-data:www-data . .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    MODEL_TYPE=local \
    GUNICORN_CMD_ARGS="--timeout 120 --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000"

# Install gunicorn and uvicorn in the runtime stage
RUN pip install --no-cache-dir gunicorn uvicorn[standard] && \
    # Create necessary directories with correct permissions
    mkdir -p /app/vector_store && \
    # Set proper ownership and permissions
    chown -R www-data:www-data /app && \
    chmod -R 755 /app && \
    # Ensure gunicorn is in PATH
    ln -s /usr/local/bin/gunicorn /usr/bin/gunicorn

# Expose the port the app runs on
EXPOSE $PORT

# Use www-data user (standard for Azure App Service)
USER www-data

# The command to run the application
CMD ["gunicorn", "app.main:app"]
