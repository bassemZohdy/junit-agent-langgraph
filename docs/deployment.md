# JUnit Agent LangGraph - Deployment Guide

**Version**: 1.0.0
**Last Updated**: February 21, 2026

This guide covers deploying JUnit Agent LangGraph in production environments, including Docker setup, monitoring, and scaling considerations.

## Table of Contents

1. [Production Deployment Checklist](#production-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Logging Setup](#logging-setup)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Scaling Guidelines](#scaling-guidelines)
7. [Rollback Procedures](#rollback-procedures)
8. [Security Best Practices](#security-best-practices)

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`py run_tests.py --all`)
- [ ] Security audit completed (Bandit, Safety)
- [ ] Dependencies updated to latest stable versions
- [ ] Configuration reviewed and hardened
- [ ] Backup procedures in place
- [ ] Monitoring tools configured
- [ ] Rollback procedure tested
- [ ] Documentation updated

### Infrastructure

- [ ] Server meets minimum requirements (8GB RAM, 4 CPU cores)
- [ ] Docker installed and configured (if using containers)
- [ ] Ollama service running and accessible
- [ ] Network ports configured (11434 for Ollama)
- [ ] SSL/TLS certificates (if HTTPS required)
- [ ] Firewall rules configured
- [ ] Load balancer configured (if scaling)

### Application

- [ ] Virtual environment created and tested
- [ ] Environment variables set in production config
- [ ] Log files directory created with proper permissions
- [ ] Temp directory for cache with sufficient space
- [ ] Database connection strings (if using external DB)
- [ ] API keys and secrets secured
- [ ] Service user created with minimal permissions

### Monitoring

- [ ] Application performance monitoring (APM) setup
- [ ] Log aggregation configured (ELK, Splunk, etc.)
- [ ] Alerting rules configured
- [ ] Health check endpoint monitored
- [ ] Error tracking (Sentry, etc.) configured
- [ ] Metrics collection (Prometheus, etc.)

---

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
# Multi-stage build for JUnit Agent
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Create non-root user
RUN useradd -m -u 1000 junitagent && \
    chown -R junitagent:junitagent /app
USER junitagent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (if using web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.config import settings; print('OK')"

# Run application
CMD ["python", "-m", "src.main"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  junit-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: junit-agent
    restart: unless-stopped
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.2
      - LOG_LEVEL=INFO
      - CACHE_ENABLED=true
    volumes:
      # Mount Java projects
      - ./projects:/app/projects:ro
      # Mount cache
      - junit-agent-cache:/app/cache
      # Mount logs
      - ./logs:/app/logs
    depends_on:
      - ollama
    networks:
      - junit-net

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - junit-net

volumes:
  junit-agent-cache:
  ollama-data:

networks:
  junit-net:
    driver: bridge
```

### Building and Running

```bash
# Build the image
docker build -t junit-agent:1.0.0 .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f junit-agent

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production Dockerfile (Optimized)

```dockerfile
# Optimized for smaller image size and security
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Make sure scripts are executable
RUN chmod +x dist/scripts/*.sh

# Create user
RUN useradd -m -u 1000 junitagent && \
    chown -R junitagent:junitagent /app

# Set PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER junitagent

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-m", "src.main"]
```

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=4096

# Timeouts (production: longer for large projects)
LLM_TIMEOUT_SECONDS=300
MAVEN_TIMEOUT_SECONDS=900

# Retry Configuration
MAX_RETRIES=5
RETRY_DELAY_SECONDS=2

# Directory Configuration
TEST_SOURCE_DIR=src/test/java
TEST_OUTPUT_DIR=target/test-classes
SOURCE_DIR=src/main/java
OUTPUT_DIR=target/classes

# Feature Flags
SKIP_TESTS=false
CACHE_ENABLED=true
PARALLEL_FILE_OPERATIONS=true

# Logging (production: WARNING or ERROR)
LOG_LEVEL=WARNING
LOG_FILE=/var/log/junit-agent/app.log

# Security
READ_ONLY_MODE=false
ENABLE_AUDIT_LOGGING=true

# Performance
MAX_CONCURRENT_OPERATIONS=10
CACHE_TTL_SECONDS=3600
```

### Environment-Specific Files

```bash
# Development
.env.development
LOG_LEVEL=DEBUG
CACHE_ENABLED=true

# Testing
.env.testing
LOG_LEVEL=INFO
SKIP_TESTS=false

# Production
.env.production
LOG_LEVEL=WARNING
CACHE_ENABLED=true
ENABLE_AUDIT_LOGGING=true
```

### Using Environment Files

```bash
# Load specific environment
export $(cat .env.production | xargs)

# Or use with docker-compose
docker-compose --env-file .env.production up -d
```

---

## Logging Setup

### Log Configuration

Configure logging in `.env`:

```bash
LOG_LEVEL=WARNING
LOG_FILE=/var/log/junit-agent/app.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### Log Rotation Setup (Linux)

Create `/etc/logrotate.d/junit-agent`:

```
/var/log/junit-agent/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 junitagent junitagent
    postrotate
        systemctl reload junit-agent > /dev/null 2>&1 || true
    endscript
}
```

### Centralized Logging

#### Using ELK Stack

```python
# In logging configuration
import logging
from logging.handlers import SysLogHandler

# Send logs to ELK
elk_handler = SysLogHandler(
    address=('elk-server', 514),
    facility=SysLogHandler.LOG_LOCAL0
)
elk_handler.setLevel(logging.INFO)
logger.addHandler(elk_handler)
```

#### Using CloudWatch (AWS)

```python
import boto3
from watchtower import CloudWatchLogHandler

cloudwatch_handler = CloudWatchLogHandler(
    log_group='junit-agent',
    stream_name='production',
    boto3_client=boto3.client('logs')
)
logger.addHandler(cloudwatch_handler)
```

### Log Formats

```python
# Structured logging format
{
    "timestamp": "2026-02-21T10:30:45Z",
    "level": "INFO",
    "service": "junit-agent",
    "environment": "production",
    "component": "TestGenerator",
    "message": "Generated 5 tests for com.example.Calculator",
    "metadata": {
        "project_path": "/projects/calc",
        "class": "Calculator",
        "duration_ms": 15420
    }
}
```

---

## Monitoring and Alerting

### Health Check Endpoint

Create a health check endpoint (if using web interface):

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    checks = {
        "status": "healthy",
        "ollama": check_ollama_connection(),
        "disk_space": check_disk_space(),
        "cache_status": check_cache(),
    }

    if all(checks.values()):
        return JSONResponse(status_code=200, content=checks)
    else:
        return JSONResponse(status_code=503, content=checks)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
test_generation_total = Counter(
    'junit_agent_tests_generated_total',
    'Total number of tests generated',
    ['project', 'success']
)

test_generation_duration = Histogram(
    'junit_agent_test_generation_duration_seconds',
    'Time taken to generate tests'
)

cache_hits = Gauge(
    'junit_agent_cache_hits',
    'Number of cache hits'
)
```

### Alerting Rules (Prometheus)

Create `alert_rules.yml`:

```yaml
groups:
  - name: junit_agent
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(junit_agent_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/second"

      - alert: OllamaUnresponsive
        expr: up{job="ollama"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Ollama service is down"
          description: "Ollama has been down for more than 2 minutes"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes{job="junit-agent"} > 1073741824
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }} bytes"
```

### Grafana Dashboard

Create a dashboard with:
- Test generation rate over time
- Average test generation duration
- Success/failure ratio
- Ollama response time
- Memory and CPU usage
- Cache hit rate

---

## Scaling Guidelines

### Horizontal Scaling

Deploy multiple instances behind a load balancer:

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  junit-agent:
    deploy:
      replicas: 3
    # ... other config
```

### Load Balancer Configuration (NGINX)

```nginx
upstream junit_agent_backend {
    least_conn;
    server junit-agent-1:8000;
    server junit-agent-2:8000;
    server junit-agent-3:8000;
}

server {
    listen 80;
    server_name junit-agent.example.com;

    location / {
        proxy_pass http://junit_agent_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Vertical Scaling

Increase resources for larger projects:

```bash
# Docker resource limits
docker run \
    --memory="8g" \
    --cpus="4" \
    junit-agent:1.0.0
```

### Database Connection Pooling

If using external database for state:

```python
# Connection pool configuration
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600
```

---

## Rollback Procedures

### Version Tagging

```bash
# Tag current version
git tag v1.0.0
git push origin v1.0.0

# Create new release branch
git checkout -b release/v1.1.0
```

### Docker Rollback

```bash
# Keep previous version
docker tag junit-agent:1.0.0 junit-agent:previous

# Deploy new version
docker build -t junit-agent:1.1.0 .
docker-compose up -d

# If issues, rollback
docker-compose down
docker tag junit-agent:previous junit-agent:latest
docker-compose up -d
```

### Database Rollback

If using state persistence:

```bash
# Backup before upgrade
cp /var/lib/junit-agent/state.db /var/lib/junit-agent/state.db.backup

# Restore if needed
cp /var/lib/junit-agent/state.db.backup /var/lib/junit-agent/state.db
```

### Configuration Rollback

```bash
# Backup production config
cp .env.production .env.production.backup

# Restore if needed
cp .env.production.backup .env.production
```

---

## Security Best Practices

### Secrets Management

Never commit secrets to git. Use:

```bash
# HashiCorp Vault
vault kv get secret/junit-agent/api-keys

# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id junit-agent/keys

# Kubernetes Secrets
kubectl create secret generic junit-agent-secrets \
  --from-literal=api-key='your-key'
```

### Network Security

```yaml
# docker-compose.yml with network restrictions
services:
  junit-agent:
    networks:
      - internal
    # No external ports exposed
  ollama:
    networks:
      - internal

networks:
  internal:
    internal: true  # No external access
```

### File Permissions

```bash
# Set restrictive permissions
chmod 600 .env.production
chmod 700 /var/log/junit-agent
chown -R junitagent:junitagent /var/lib/junit-agent
```

### Input Validation

All inputs should be validated:

```python
# Already implemented in validation.py
from src.utils.validation import validate_path
from src.utils.security import SecurityUtils

# Sanitize all user inputs
safe_path = SecurityUtils.sanitize_path(user_input)
```

### Rate Limiting

Prevent abuse:

```python
from src.utils.concurrent import RateLimiter

rate_limiter = RateLimiter(max_requests=100, time_window=60)

@rate_limiter.limit
def process_request(request):
    # Process request
    pass
```

### Audit Logging

Enable audit logging for compliance:

```bash
# In .env.production
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_FILE=/var/log/junit-agent/audit.log
```

---

## Production Deployment Example

### Complete Deployment Script

```bash
#!/bin/bash

# deploy.sh - Production deployment script

set -e

echo "Starting JUnit Agent deployment..."

# Pull latest code
git pull origin main

# Backup current version
cp -r /var/www/junit-agent /var/www/junit-agent.backup.$(date +%Y%m%d)

# Build new version
docker build -t junit-agent:latest .

# Run tests
docker run --rm junit-agent:latest python -m pytest tests/

# Stop current version
docker-compose down

# Start new version
docker-compose up -d

# Wait for health check
sleep 30

# Verify deployment
if curl -f http://localhost:8000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed! Rolling back..."
    docker-compose down
    docker tag junit-agent:previous junit-agent:latest
    docker-compose up -d
    exit 1
fi

# Clean up old backups
find /var/www/junit-agent.backup.* -mtime +7 -delete

echo "Deployment complete!"
```

---

## Maintenance

### Regular Tasks

- **Daily**: Check log files for errors
- **Weekly**: Review disk usage and clear cache
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full security audit and performance review

### Backup Strategy

```bash
# Automated backup script
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/junit-agent/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup configuration
cp .env.production "$BACKUP_DIR/"

# Backup state
tar -czf "$BACKUP_DIR/state.tar.gz" /var/lib/junit-agent/

# Backup logs
tar -czf "$BACKUP_DIR/logs.tar.gz" /var/log/junit-agent/

# Keep for 30 days
find /backups/junit-agent -mtime +30 -delete
```

---

**Version**: 1.0.0
**Last Updated**: February 21, 2026
**Maintained By**: JUnit Agent Team
