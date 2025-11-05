# 🚀 LemonDocker Quick Start Guide

## Step 1: Build the Docker Image

```bash
cd LemonDocker
docker build -t lemondocker:v2 .
```

This will take ~30 minutes as it installs 50+ security tools.

## Step 2: Run the Container

```bash
docker run -d \
  --name lemondocker \
  -p 8000:8000 \
  -p 5555:5555 \
  -v $(pwd)/results:/opt/results \
  lemondocker:v2
```

**Ports:**
- `8000` - Main API
- `5555` - Flower (Celery monitoring UI)

**Volume:**
- `./results` - All scan results stored here

## Step 3: Wait for Initialization

First run will initialize database and seed pipelines (~2 minutes):

```bash
# Follow logs
docker logs -f lemondocker

# Wait for this message:
# "✓ Initialization Complete!"
```

## Step 4: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "celery": "connected",
  "tools_available": 50,
  "pipelines_available": 9
}
```

## Step 5: View Available Pipelines

```bash
curl http://localhost:8000/pipelines/ | jq .
```

You should see 9 pipelines:
1. SUBDOMAIN_DISCOVERY_COMPLETE
2. FULL_RECON_PIPELINE
3. CONTENT_DISCOVERY_DEEP
4. VULNERABILITY_SCAN_COMPREHENSIVE
5. PORT_SCAN_COMPLETE
6. JAVASCRIPT_RECON_PIPELINE
7. CLOUD_ASSETS_DISCOVERY
8. CONTINUOUS_MONITORING
9. QUICK_SCAN

## Step 6: Run Your First Scan

Let's start with a quick scan:

```bash
curl -X POST http://localhost:8000/executions/start \
  -H 'Content-Type: application/json' \
  -d '{
    "pipeline_id": 9,
    "target": "example.com",
    "user_id": "demo"
  }' | jq .
```

**Response:**
```json
{
  "execution_id": "abc-123-def-456",
  "celery_task_id": "task-789",
  "results_path": "/opt/results/demo/example.com/example.com/abc-123-def-456",
  "status_url": "/executions/abc-123-def-456/status"
}
```

## Step 7: Monitor Progress

```bash
# Save execution ID
EXECUTION_ID="abc-123-def-456"

# Check status
curl http://localhost:8000/executions/$EXECUTION_ID/status | jq .
```

**Or** use Flower UI: http://localhost:5555

## Step 8: Get Results

```bash
# Summary
curl http://localhost:8000/results/$EXECUTION_ID/summary | jq .

# All subdomains
curl http://localhost:8000/results/$EXECUTION_ID/subdomains | jq .

# Vulnerabilities
curl http://localhost:8000/results/$EXECUTION_ID/vulnerabilities | jq .

# Export everything to JSON
curl http://localhost:8000/results/$EXECUTION_ID/export -o scan_results.json
```

## Step 9: Access Results Files

```bash
# Results are in ./results directory
ls -la ./results/demo/example.com/

# View raw tool outputs
cat ./results/demo/example.com/example.com/abc-123-def-456/subfinder.txt
cat ./results/demo/example.com/example.com/abc-123-def-456/nuclei_vulns.json
```

---

## 🎯 Common Workflows

### Full Reconnaissance on a Target

```bash
curl -X POST http://localhost:8000/executions/start \
  -H 'Content-Type: application/json' \
  -d '{
    "pipeline_id": 2,
    "target": "hackerone.com",
    "user_id": "security_team",
    "metadata": {"project": "Q1_Audit"}
  }'
```

This will:
- Discover all subdomains (10+ tools)
- Verify live hosts
- Scan ports
- Crawl for URLs
- Detect technologies
- Scan for vulnerabilities
- Take screenshots

**Duration:** ~45 minutes (with parallel execution)

### Content Discovery Only

```bash
# First, get list of live hosts
echo -e "https://site1.example.com\nhttps://site2.example.com" > hosts.txt

# Upload to container
docker cp hosts.txt lemondocker:/tmp/hosts.txt

# Run content discovery
curl -X POST http://localhost:8000/executions/start \
  -d '{
    "pipeline_id": 3,
    "target": "example.com",
    "input_file": "/tmp/hosts.txt"
  }'
```

### Continuous Monitoring (Daily Cron)

```bash
#!/bin/bash
# Add to crontab: 0 0 * * * /path/to/daily_scan.sh

EXECUTION=$(curl -s -X POST http://localhost:8000/executions/start \
  -H 'Content-Type: application/json' \
  -d '{
    "pipeline_id": 8,
    "target": "company.com",
    "user_id": "monitor"
  }')

EXEC_ID=$(echo $EXECUTION | jq -r .execution_id)

# Wait for completion (check every 5 minutes)
while true; do
  STATUS=$(curl -s http://localhost:8000/executions/$EXEC_ID/status | jq -r .status)
  if [ "$STATUS" = "COMPLETED" ]; then
    # Check for new findings
    NEW_SUBS=$(curl -s http://localhost:8000/results/$EXEC_ID/subdomains | jq '.total_subdomains')
    echo "Found $NEW_SUBS new subdomains on $(date)"

    # Send alert if vulnerabilities found
    VULNS=$(curl -s http://localhost:8000/results/$EXEC_ID/vulnerabilities | jq '.total_vulnerabilities')
    if [ "$VULNS" -gt 0 ]; then
      echo "ALERT: $VULNS vulnerabilities found!"
      # Send to Slack/email/etc
    fi
    break
  fi
  sleep 300
done
```

---

## 🔧 Management Commands

```bash
# List pipelines
docker exec lemondocker lemondocker list-pipelines

# List tools
docker exec lemondocker lemondocker list-tools

# Check system status
docker exec lemondocker lemondocker status

# Cleanup old executions (>30 days)
docker exec lemondocker lemondocker cleanup

# Test a pipeline
docker exec lemondocker lemondocker test-pipeline QUICK_SCAN example.com

# Open Python shell
docker exec -it lemondocker lemondocker shell
```

---

## 📊 Swagger Documentation

Full API documentation available at: **http://localhost:8000/swagger/**

Interactive API explorer with:
- All endpoints documented
- Request/response examples
- Try it out functionality
- Schema definitions

---

## ⚙️ Configuration (Optional)

### Add API Keys for Better Results

```bash
# Chaos (ProjectDiscovery datasets)
curl -X POST http://localhost:8000/config/env \
  -H 'Content-Type: application/json' \
  -d '{
    "key": "CHAOS_KEY",
    "value": "your_api_key_here",
    "is_sensitive": true
  }'

# GitHub Token
curl -X POST http://localhost:8000/config/env \
  -d '{
    "key": "GITHUB_TOKEN",
    "value": "ghp_your_token_here",
    "is_sensitive": true
  }'
```

See `.env.example` for all available configurations.

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs lemondocker

# Common issues:
# - Port 8000 already in use: docker run -p 8080:8000 ...
# - Port 5555 already in use: docker run -p 5556:5555 ...
```

### API returns "unhealthy"
```bash
# Check Redis
docker exec lemondocker redis-cli ping

# Check Celery workers
docker exec lemondocker celery -A celery_config inspect stats

# Restart container
docker restart lemondocker
```

### Execution stuck in RUNNING
```bash
# Check Celery logs
docker exec lemondocker cat /opt/results/celery_pipelines.log
docker exec lemondocker cat /opt/results/celery_steps.log

# Cancel execution
curl -X POST http://localhost:8000/executions/$EXECUTION_ID/cancel
```

### No results found
```bash
# Check execution status
curl http://localhost:8000/executions/$EXECUTION_ID/status

# Look for errors in step executions
# Check raw output files
ls -la ./results/[user_id]/[target]/[asset]/[execution_id]/
```

---

## 📚 Next Steps

1. **Read Full Documentation**: `README_API_V2.md`
2. **Configure API Keys**: See `.env.example`
3. **Customize Pipelines**: See `api/seed_data.py`
4. **Integrate with CI/CD**: Use API endpoints
5. **Setup Monitoring**: Configure alerting for new findings

---

## 🎉 You're Ready!

You now have a **production-ready reconnaissance automation platform** running!

Key features:
- ✅ 9 professional pipelines
- ✅ 50+ security tools
- ✅ Parallel execution (4x faster)
- ✅ Structured results
- ✅ Real-time monitoring

Happy hunting! 🚀
