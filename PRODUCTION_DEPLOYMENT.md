# Production Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the Predictive Infrastructure Intelligence system to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Production Configuration](#production-configuration)
4. [Deployment Options](#deployment-options)
5. [Security Hardening](#security-hardening)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

- [ ] Code review completed
- [ ] All tests pass (`pytest`)
- [ ] Security scan completed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Rollback plan in place
- [ ] Backup strategy defined
- [ ] Monitoring and alerting configured
- [ ] Log aggregation setup
- [ ] SSL/TLS certificates obtained

## Environment Setup

### 1. System Requirements

```bash
# Minimum requirements
- Python 3.9+
- 2 CPU cores
- 2GB RAM
- 20GB disk space

# Recommended for production
- Python 3.11+
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ disk space
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac
source venv/bin/activate
# On Windows
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip wheel setuptools

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with production values
vim .env

# Critical settings to configure:
export FLASK_ENV=production
export FLASK_DEBUG=False
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export LOG_LEVEL=WARNING
export ENABLE_AUTO_REMEDIATION=True
export CORS_ORIGINS=your-domain.com
```

## Production Configuration

### 1. Application Settings

```python
# .env
FLASK_ENV=production
FLASK_DEBUG=False
TESTING=False
APP_NAME="Infrastructure Intelligence Production"

# Logging - more restrictive in production
LOG_LEVEL=WARNING
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Performance tuning
MONITORING_INTERVAL=5        # Check every 5 seconds in production
MAX_HISTORY_RECORDS=5000     # Keep more historical data
MAX_WORKERS=4                # Number of gunicorn workers

# Security
REQUEST_TIMEOUT=60
API_TIMEOUT=30
API_RATE_LIMIT=1000
```

### 2. Kubernetes Configuration

```bash
# Set correct namespace
export K8S_NAMESPACE=production

# Configure kubeconfig if not using in-cluster config
export KUBECONFIG=/path/to/production/kubeconfig
```

### 3. Risk Detection Thresholds

```bash
# Configure for production environment
export RISK_THRESHOLD_CRITICAL=70.0    # Trigger critical alerts at 70%
export RISK_THRESHOLD_WARNING=50.0     # Warning at 50%
```

## Deployment Options

### Option 1: Docker Deployment (Recommended)

```bash
# Build image
docker build -t infra-intelligence:latest .

# Run container
docker run -d \
  --name infra-intelligence \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e K8S_NAMESPACE=production \
  --volume /path/to/kubeconfig:/home/kubeconfig:ro \
  infra-intelligence:latest

# Verify running
docker logs infra-intelligence
curl http://localhost:5000/api/health
```

### Option 2: Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f kubernetes-manifest.yaml

# Verify deployment
kubectl get pods -n production
kubectl logs -f deployment/infra-intelligence -n production

# Check service
kubectl get svc infra-intelligence -n production
```

### Option 3: Standalone Systemd Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/infra-intelligence.service > /dev/null <<EOF
[Unit]
Description=Infrastructure Intelligence Service
After=network.target

[Service]
Type=notify
User=infra
WorkingDirectory=/opt/infra-intelligence
Environment="FLASK_ENV=production"
ExecStart=/opt/infra-intelligence/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 60 \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable infra-intelligence
sudo systemctl start infra-intelligence

# Check status
sudo systemctl status infra-intelligence
```

## Security Hardening

### 1. Network Security

```bash
# Use firewall to restrict access
sudo ufw allow 5000/tcp from trusted_network

# Enable HTTPS with ngin proxy or load balancer
# Configure SSL/TLS certificates
```

### 2. Application Security

```python
# In production config (.env):
CORS_ORIGINS=your-trusted-domain.com
ENABLE_DEBUG=False
REQUEST_TIMEOUT=60
```

### 3. Kubernetes Security

```yaml
# In kubernetes-manifest.yaml, add security context:
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

### 4. API Authentication (Optional)

```python
# Implement token-based authentication
from functools import wraps
from flask import request

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not validate_token(token):
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/secret', methods=['POST'])
@require_token
def secret_endpoint():
    return {'data': 'sensitive'}
```

## Monitoring & Maintenance

### 1. Health Checks

```bash
# Manual health check
curl -s http://localhost:5000/api/health | jq .

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-02-17T10:30:00",
#   "components": {
#     "kubernetes": "available",
#     "ml_engine": "ready",
#     "monitoring": "running"
#   }
# }
```

### 2. Monitoring Setup

```bash
# Enable Prometheus metrics
# Add to docker-compose or kubernetes deployment:
- name: ENABLE_METRICS
  value: "true"

# Scrape metrics every 30 seconds
# Add to Prometheus config:
- job_name: 'infra-intelligence'
  static_configs:
    - targets: ['localhost:5000']
  metrics_path: '/metrics'
```

### 3. Log Aggregation

```bash
# Send logs to centralized logging system
# Configure in app.py to send to:
- Elasticsearch/ELK stack
- Splunk
- CloudWatch
- Papertrail

# Example: Send to Elasticsearch
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

### 4. Alerting Configuration

```yaml
# Example alert rules (Prometheus):
- alert: HighRiskDetectionRate
  expr: rate(risks_detected_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High risk detection rate"
    
- alert: ServiceDown
  expr: up{job="infra-intelligence"} == 0
  for: 1m
  annotations:
    summary: "Infrastructure Intelligence service is down"
```

## Troubleshooting

### Issue: Service won't start

```bash
# Check logs
docker logs infra-intelligence
# or
journalctl -u infra-intelligence -n 50

# Verify configuration
python -c "from config import config; print(config.get_summary())"

# Check port availability
lsof -i :5000
```

### Issue: High memory usage

```bash
# Monitor memory
docker stats infra-intelligence
# or
ps aux | grep gunicorn

# Reduce cache size
export MAX_HISTORY_RECORDS=1000

# Restart service to free memory
docker restart infra-intelligence
```

### Issue: Kubernetes connection errors

```bash
# Verify kubeconfig
kubectl config view
kubectl cluster-info

# Check in-cluster authentication
kubectl auth can-i list nodes --as=system:serviceaccount:default:infra

# View service account
kubectl get sa infra-intelligence -o yaml
```

### Issue: API timeouts

```bash
# Increase timeout
export REQUEST_TIMEOUT=120
export API_TIMEOUT=60

# Check backend performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/stats
```

## Performance Tuning

```python
# Optimize for production loads:

# 1. Increase worker processes
WORKERS = 8  # Match CPU cores

# 2. Adjust monitoring interval
MONITORING_INTERVAL = 5  # Seconds

# 3. Enable caching
CACHE_ENABLED = True
CACHE_TTL = 60

# 4. Limit history retention
MAX_HISTORY_RECORDS = 5000

# 5. Batch database operations
DB_BATCH_SIZE = 100
```

## Backup & Recovery

```bash
# Backup configuration and state
tar czf backup_$(date +%Y%m%d).tar.gz \
    .env \
    app.log \
    audit_log.json

# Store in secure location
mv backup_*.tar.gz /backup/infra-intelligence/

# Recovery procedure
tar xzf /backup/infra-intelligence/backup_*.tar.gz
docker restart infra-intelligence
```

## Maintenance Windows

### Regular Tasks

- **Daily**: Review logs for errors, check health score
- **Weekly**: Review performance metrics, update dependencies
- **Monthly**: Full backup, security audit, capacity planning
- **Quarterly**: Disaster recovery drill, security assessment

### Updates

```bash
# Update dependencies safely
pip install --upgrade -r requirements.txt

# Test in staging first
python -m pytest tests/

# Deploy to production
docker-compose up -d --build
```

## Contact & Support

For production issues, contact the DevOps team or raise a ticket in the issue tracker.

---

**Last Updated**: February 17, 2026
**Version**: 1.0
**Maintained By**: Engineering Team
