#!/bin/bash

# Start Redis
redis-server &

# Add /opt/api to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/api

# Start Celery worker
celery -A celery_config worker --loglevel=info &

# Start the Flask API server
python3 /opt/api/server.py
