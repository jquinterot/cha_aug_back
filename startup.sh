#!/bin/bash
# Use the full path to Python and Uvicorn for maximum compatibility
/usr/local/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
