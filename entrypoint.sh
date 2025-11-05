#!/bin/bash

set -e

echo "=========================================="
echo "  LemonDocker Starting..."
echo "=========================================="
echo ""

# Export environment variables
export PYTHONPATH=$PYTHONPATH:/opt/api
export FLOWER_UNAUTHENTICATED_API=true

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes
sleep 2

# Wait for Redis to be ready
max_attempts=30
attempt=0
until redis-cli ping > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    echo "  Waiting for Redis... ($attempt/$max_attempts)"
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Redis failed to start"
    exit 1
fi
echo "✓ Redis started"
echo ""

# Initialize database on first run
if [ ! -f /opt/results/pipelines.db ]; then
    echo "First run detected - initializing database..."
    bash /opt/init_db.sh
else
    echo "Database exists, skipping initialization"
fi
echo ""

# Start Celery workers with multiple concurrency for parallel execution
echo "Starting Celery workers..."
# Main worker for pipeline orchestration
celery -A celery_config worker \
    --concurrency=2 \
    --queues=pipelines \
    --loglevel=INFO \
    --logfile=/opt/results/celery_pipelines.log \
    --pidfile=/tmp/celery_pipeline_worker.pid \
    --detach

# Workers for step execution (parallel steps)
celery -A celery_config worker \
    --concurrency=10 \
    --queues=steps \
    --loglevel=INFO \
    --logfile=/opt/results/celery_steps.log \
    --pidfile=/tmp/celery_step_worker.pid \
    --detach

sleep 3
echo "✓ Celery workers started"
echo "  - Pipeline queue: 2 workers"
echo "  - Steps queue: 10 workers (for parallel execution)"
echo ""

# Start Flower for monitoring
echo "Starting Flower (Celery monitoring UI)..."
celery -A celery_config flower \
    --port=5555 \
    --loglevel=INFO \
    --url_prefix=flower \
    --persistent=True \
    --db=/opt/results/flower.db \
    &

sleep 2
echo "✓ Flower started on port 5555"
echo ""

# Show configuration
echo "Configuration:"
echo "  • API Port: 8000"
echo "  • Flower Port: 5555"
echo "  • Results Path: /opt/results"
echo "  • Database: /opt/results/pipelines.db"
echo ""

# Start Flask API server (v2 by default)
echo "Starting LemonDocker API v2..."
echo "=========================================="
echo ""

# Check which server to run
if [ "$USE_LEGACY_SERVER" = "true" ]; then
    echo "Running legacy server (server.py)"
    python3 /opt/api/server.py
else
    echo "Running v2 server (server_v2.py)"
    python3 /opt/api/server_v2.py
fi
