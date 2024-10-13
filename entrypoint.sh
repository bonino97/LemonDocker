#!/bin/bash

# Start Redis
redis-server &

# Add /opt/api to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/api

# Set the environment variable for Flower API without authentication
export FLOWER_UNAUTHENTICATED_API=true

# Start Celery worker with logging to track task progress in real-time
celery -A celery_config worker --loglevel=info &

# Start Flower for Celery monitoring with unauthenticated API access
celery -A celery_config flower --port=5555 &

# Start the Flask API server
python3 /opt/api/server.py
