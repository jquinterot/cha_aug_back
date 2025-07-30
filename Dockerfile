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
    MODEL_TYPE=local

# Install uvicorn for production (system-wide for Azure compatibility)
RUN pip install --no-cache-dir uvicorn[standard]==0.30.6 && \
    # Create a symlink for Azure compatibility
    ln -sf /usr/local/bin/uvicorn /usr/bin/uvicorn

# Create necessary directories with correct permissions
RUN mkdir -p /app/vector_store && \
    # Set proper ownership and permissions
    chown -R www-data:www-data /app && \
    chmod -R 755 /app

# Switch to non-root user for running the application
USER www-data

# Set the working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE $PORT

# Copy the startup script
COPY --chown=www-data:www-data startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# The command to run the application with Uvicorn
CMD ["/usr/local/bin/startup.sh"]
