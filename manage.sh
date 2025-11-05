#!/bin/bash
# Utility script for managing LemonDocker

set -e

export PYTHONPATH=$PYTHONPATH:/opt/api

show_help() {
    cat << EOF
LemonDocker Management Utility

Usage: ./manage.sh [command]

Commands:
    init            Initialize database and seed data
    seed            Re-seed tools and pipelines
    list-pipelines  List all available pipelines
    list-tools      List all available tools
    status          Show system status
    cleanup         Cleanup old executions
    test-pipeline   Test a pipeline execution
    shell           Open Python shell with context
    help            Show this help message

Examples:
    ./manage.sh init
    ./manage.sh list-pipelines
    ./manage.sh test-pipeline QUICK_SCAN example.com
EOF
}

init_database() {
    echo "Initializing database..."
    bash /opt/init_db.sh
}

seed_database() {
    echo "Seeding database..."
    python3 /opt/api/seed_data.py
}

list_pipelines() {
    python3 << 'PYTHON_SCRIPT'
from models import get_session, Pipeline

session = get_session()
pipelines = session.query(Pipeline).filter_by(is_active=True).all()

print("\n" + "="*80)
print("  AVAILABLE PIPELINES")
print("="*80 + "\n")

for p in pipelines:
    print(f"ID: {p.id}")
    print(f"Name: {p.name}")
    print(f"Description: {p.description}")
    print(f"Category: {p.category.value if p.category else 'N/A'}")
    print(f"Steps: {len(p.steps)}")
    print(f"Est. Duration: {p.estimated_duration_minutes} minutes")
    print("-" * 80)

print(f"\nTotal: {len(pipelines)} pipelines\n")
PYTHON_SCRIPT
}

list_tools() {
    python3 << 'PYTHON_SCRIPT'
from models import get_session, Tool

session = get_session()
tools = session.query(Tool).all()

# Group by category
from collections import defaultdict
by_category = defaultdict(list)

for tool in tools:
    category = tool.category.value if tool.category else "Unknown"
    by_category[category].append(tool)

print("\n" + "="*80)
print("  AVAILABLE TOOLS")
print("="*80 + "\n")

for category in sorted(by_category.keys()):
    print(f"\n{category}:")
    print("-" * 80)
    for tool in by_category[category]:
        print(f"  • {tool.name:25} - {tool.description}")

print(f"\n\nTotal: {len(tools)} tools\n")
PYTHON_SCRIPT
}

show_status() {
    python3 << 'PYTHON_SCRIPT'
import requests
import json

try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    data = response.json()

    print("\n" + "="*80)
    print("  SYSTEM STATUS")
    print("="*80 + "\n")

    print(f"Status: {data.get('status', 'unknown').upper()}")
    print(f"Database: {data.get('database', 'unknown')}")
    print(f"Celery: {data.get('celery', 'unknown')}")
    print(f"Tools Available: {data.get('tools_available', 0)}")
    print(f"Pipelines Available: {data.get('pipelines_available', 0)}")
    print()

except Exception as e:
    print(f"\nERROR: Could not connect to API - {e}\n")
    exit(1)
PYTHON_SCRIPT
}

cleanup_old() {
    echo "Cleaning up old executions..."
    python3 << 'PYTHON_SCRIPT'
from models import get_session
from pipeline_executor import PipelineExecutor

session = get_session()
executor = PipelineExecutor(session)

count = executor.cleanup_old_executions(days_old=30)
print(f"✓ Cleaned up {count} old executions")
PYTHON_SCRIPT
}

test_pipeline() {
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Usage: ./manage.sh test-pipeline <pipeline_name> <target>"
        echo "Example: ./manage.sh test-pipeline QUICK_SCAN example.com"
        exit 1
    fi

    PIPELINE_NAME=$2
    TARGET=$3

    echo "Testing pipeline: $PIPELINE_NAME on target: $TARGET"

    python3 << PYTHON_SCRIPT
from models import get_session, Pipeline
from pipeline_executor import PipelineExecutor
import json

session = get_session()

# Find pipeline
pipeline = session.query(Pipeline).filter_by(name='$PIPELINE_NAME').first()

if not pipeline:
    print(f"ERROR: Pipeline '$PIPELINE_NAME' not found")
    exit(1)

# Validate requirements
from config_manager import get_config_manager
config = get_config_manager()
validation = config.validate_pipeline_requirements(pipeline.id)

if not validation['valid']:
    print(f"WARNING: Missing requirements: {validation['missing_required']}")

# Show execution plan
executor = PipelineExecutor(session)
plan = executor.get_execution_plan(pipeline.id)

print(f"\nExecution Plan for {pipeline.name}:")
print(json.dumps(plan, indent=2))

print(f"\nTo execute this pipeline, run:")
print(f"curl -X POST http://localhost:8000/executions/start \\\\")
print(f"  -H 'Content-Type: application/json' \\\\")
print(f"  -d '{{")
print(f"    \"pipeline_id\": {pipeline.id},")
print(f"    \"target\": \"$TARGET\",")
print(f"    \"user_id\": \"test\"")
print(f"  }}'")
print()
PYTHON_SCRIPT
}

open_shell() {
    echo "Opening Python shell with LemonDocker context..."
    python3 << 'PYTHON_SCRIPT'
from models import *
from pipeline_executor import PipelineExecutor
from config_manager import get_config_manager
from result_parsers import get_parser

session = get_session()
config = get_config_manager()
executor = PipelineExecutor(session)

print("\n" + "="*80)
print("  LemonDocker Python Shell")
print("="*80)
print("\nAvailable objects:")
print("  • session       - Database session")
print("  • config        - Configuration manager")
print("  • executor      - Pipeline executor")
print("  • Pipeline      - Pipeline model")
print("  • Tool          - Tool model")
print("  • Execution     - Execution model")
print("\nExample:")
print("  pipelines = session.query(Pipeline).all()")
print("  for p in pipelines: print(p.name)")
print()

import code
code.interact(local=locals())
PYTHON_SCRIPT
}

# Main command handler
case "$1" in
    init)
        init_database
        ;;
    seed)
        seed_database
        ;;
    list-pipelines)
        list_pipelines
        ;;
    list-tools)
        list_tools
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup_old
        ;;
    test-pipeline)
        test_pipeline "$@"
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
