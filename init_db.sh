#!/bin/bash
# Initialize LemonDocker database and seed data

set -e

echo "=========================================="
echo "  LemonDocker Initialization"
echo "=========================================="
echo ""

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/api

# Wait for Redis to be ready
echo "Waiting for Redis..."
max_attempts=30
attempt=0
until redis-cli ping > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    echo "  Redis not ready, waiting... ($attempt/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Redis failed to start"
    exit 1
fi

echo "✓ Redis is ready"
echo ""

# Initialize database
echo "Initializing database..."
cd /opt/api

python3 << 'PYTHON_SCRIPT'
from models import init_db, get_session
from config_manager import get_config_manager

print("  Creating database tables...")
init_db()
print("  ✓ Database tables created")

print("  Creating default configurations...")
config_manager = get_config_manager()
config_manager.create_default_configs()
print("  ✓ Default configurations created")

print("\nDatabase initialization complete!")
PYTHON_SCRIPT

echo ""

# Seed database with tools and pipelines
echo "Seeding tools and pipelines..."
python3 /opt/api/seed_data.py

echo ""
echo "=========================================="
echo "  ✓ Initialization Complete!"
echo "=========================================="
echo ""
echo "Available endpoints:"
echo "  • API Docs:    http://localhost:8000/swagger/"
echo "  • Health:      http://localhost:8000/health"
echo "  • Pipelines:   http://localhost:8000/pipelines/"
echo "  • Flower UI:   http://localhost:5555"
echo ""
