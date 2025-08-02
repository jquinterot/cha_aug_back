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

# Create cache directories with proper permissions
RUN mkdir -p /app/.cache/huggingface /app/.cache/torch /app/.cache/sentence_transformers && \
    chown -R www-data:www-data /app/.cache && \
    chmod -R 755 /app/.cache

# Copy application code (excluding dependencies from builder)
COPY --chown=www-data:www-data . .

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    MODEL_TYPE=local \
    # Set Hugging Face cache directories
    TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers \
    HF_DATASETS_CACHE=/app/.cache/huggingface/datasets \
    HF_HOME=/app/.cache/huggingface \
    TORCH_HOME=/app/.cache/torch \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

# Install Python dependencies directly in the final image (not from builder)
USER root
RUN pip install --no-cache-dir -r requirements.txt && \
    # Install uvicorn system-wide for Azure compatibility
    pip install --no-cache-dir uvicorn[standard]==0.30.6 && \
    # Create symlinks for Azure compatibility
    ln -sf /usr/local/bin/uvicorn /usr/bin/uvicorn && \
    ln -sf /usr/local/bin/uvicorn /usr/local/bin/uvicorn3 && \
    # Verify installations
    python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')" && \
    # Clean up to reduce image size
    pip cache purge && \
    rm -rf /root/.cache/pip

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

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# The command to run the application with Uvicorn
CMD ["/usr/local/bin/startup.sh"]
