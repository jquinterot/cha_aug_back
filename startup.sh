#!/bin/bash

# Set environment variables if not already set
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Set Hugging Face cache directories
export TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers
export HF_DATASETS_CACHE=/app/.cache/huggingface/datasets
export HF_HOME=/app/.cache/huggingface
export TORCH_HOME=/app/.cache/torch
export SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

# Create cache directories if they don't exist
mkdir -p $TRANSFORMERS_CACHE $HF_DATASETS_CACHE $TORCH_HOME $SENTENCE_TRANSFORMERS_HOME
chown -R www-data:www-data /app/.cache
chmod -R 755 /app/.cache

# Debug: Print environment variables
echo "=== Environment Variables ==="
printenv | grep -E 'PYTHON|TRANSFORMERS|HF_|TORCH|SENTENCE'

# Debug: Check directory permissions
echo -e "\n=== Directory Permissions ==="
ls -la /app/.cache

# Start the application
echo -e "\n=== Starting Application ==="
exec /usr/local/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
