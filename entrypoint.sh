#!/bin/bash

# Start Redis
redis-server &

# Start Celery worker
celery -A api.celery_config worker --loglevel=info &

# Start the Flask API server
python3 /opt/api/server.py
