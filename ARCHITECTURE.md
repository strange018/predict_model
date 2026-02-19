# Production Architecture & Best Practices

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client / Dashboard                        │
│              (Vue.js / React SPA on http/https)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS (REST API)
                         │
┌─────────────────────────┴────────────────────────────────────┐
│                  Load Balancer / Nginx                       │
│              (SSL Termination, Rate Limiting)                │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───┴──┐         ┌───┴──┐         ┌──┴───┐
    │ Pod  │         │ Pod  │         │ Pod  │
    │  #1  │         │  #2  │         │  #3  │
    └───┬──┘         └───┬──┘         └──┬───┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ├─ Monitoring Service (3s intervals)
                         ├─ ML Decision Engine (Degradation prediction)
                         ├─ Health Scorer (5-component weighted scoring)
                         ├─ Analytics Engine (Cluster metrics)
                         ├─ Event Manager (Structured logging)
                         └─ Audit Logger (Compliance tracking)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────┴─────┐   ┌────┴─────┐   ┌────┴─────┐
    │ Kubernetes API  │ etcd │ Prometheus │
    │               │   (State) │ (Metrics) │
    └────────────┘   └──────────┘   └──────────┘
```

## Component Responsibilities

### Frontend (index.html / script.js / styles.css)
- **Purpose**: Real-time infrastructure monitoring dashboard
- **Technology**: Vanilla JavaScript, responsive CSS
- **Polling**: Stats (1s), Nodes (1.5s), Events (0.8s), Analytics (2s)
- **Updates**: Live metrics, health indicators, event log

### Backend API (app.py)
- **Framework**: Flask with CORS
- **Endpoints**: 20+ RESTful endpoints
- **Rate Limit**: 1000 req/min per IP
- **Timeout**: 30s per request
- **Workers**: 4 (configurable)

### Kubernetes Integration (kubernetes_manager.py)
- **Mode**: Hybrid (Real cluster + DEMO mode)
- **Operations**: Taint, drain, cordon nodes
- **Monitoring**: Fetch metrics, pod counts
- **Fallback**: Graceful degradation to DEMO mode

### ML Engine (ml_decision_engine.py)
- **Model**: Pre-trained on synthetic infrastructure data
- **Input**: CPU, Memory, Temperature, Latency, Disk I/O
- **Output**: Risk score (0-100), degradation prediction
- **Update**: Monthly retraining with new data

### Health Scorer (health_scorer.py)
- **Metrics**: 5 weighted components
- **Weights**: CPU 25%, Memory 25%, Temp 20%, Latency 15%, Disk 15%
- **Grades**: A+ to F (100 to 0+)
- **Status**: Healthy, Degraded, Critical
- **Thresholds**: Tunable per environment

### Analytics Engine (analytics_engine.py)
- **Metrics**: Cluster-wide aggregation
- **History**: Last 1000 records (5000+ in production)
- **Trend**: 3-point moving average + polynomial regression
- **Risk Detection**: Counts healthy/degraded/critical nodes

### Event Manager (event_manager.py)
- **Events**: Risk, Action, Info, Warning types
- **Storage**: In-memory deque (1000 max)
- **Filtering**: By type and time range
- **Export**: JSON format

## Performance Characteristics

### Scalability
- **Nodes**: Handles 500+ nodes
- **Pods**: Tracks 10,000+ pods
- **Events**: Stores 1,000 recent events
- **Monitoring**: 3-5 second intervals

### Response Times (Target)
- Health check: < 100ms
- Stats endpoint: < 200ms
- Nodes endpoint: < 500ms
- Analytics: < 300ms

### Resource Usage (Single Instance)
- **Memory**: 200-500MB (varies with history size)
- **CPU**: 0.5-1.0 core during monitoring cycles
- **Disk**: 100MB (logs + state)

## Deployment Patterns

### Option 1: Kubernetes Deployment (Recommended)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infra-intelligence
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: infra-intelligence
  template:
    metadata:
      labels:
        app: infra-intelligence
    spec:
      serviceAccountName: infra-intelligence
      containers:
      - name: app
        image: infra-intelligence:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: LOG_LEVEL
          value: "WARNING"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Option 2: Docker Compose (Development/Testing)
```yaml
version: '3.8'
services:
  infra-intelligence:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      LOG_LEVEL: INFO
    volumes:
      - ./app.log:/app/app.log
    restart: unless-stopped
```

### Option 3: Systemd Service (Single Machine)
```ini
[Unit]
Description=Infrastructure Intelligence
After=network.target

[Service]
Type=notify
User=infra-user
WorkingDirectory=/opt/infra-intelligence
ExecStart=/opt/infra-intelligence/venv/bin/gunicorn \
    --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Best Practices

### Authentication & Authorization
```python
# API Token validation
VALID_TOKENS = set(os.getenv('API_TOKENS', '').split(','))

@app.before_request
def validate_token():
    if request.path.startswith('/api/'):
        token = request.headers.get('X-API-Token')
        if token not in VALID_TOKENS:
            return {'error': 'Unauthorized'}, 401
```

### Network Security
- Use HTTPS/TLS for all external communications
- Restrict Kubernetes API access
- Firewall off monitoring ports
- Use VPN for remote access

### Data Protection
- Encrypt sensitive data at rest
- Use short-lived tokens
- Audit all operations
- Regular backups

## Monitoring & Observability

### Logging Levels
- **DEBUG**: Development only, detailed traces
- **INFO**: Key operations, startup/shutdown
- **WARNING**: Unusual conditions, recoverable errors
- **ERROR**: Serious problems requiring attention
- **CRITICAL**: System failures

### Metrics to Track
```prometheus
# Application metrics
infra_risks_detected_total
infra_workloads_moved_total
infra_nodes_monitored
infra_health_score{node_id}
infra_api_request_duration_seconds
infra_api_errors_total

# System metrics
process_memory_bytes
process_cpu_seconds_total
python_gc_collections_total
```

### Alerting Rules
```yaml
- alert: HighRiskDetectionRate
  expr: rate(infra_risks_detected_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High risk detection rate"

- alert: ServiceDown
  expr: up{job="infra-intelligence"} == 0
  for: 1m
  annotations:
    summary: "Service is down"

- alert: HighMemoryUsage
  expr: process_memory_bytes > 512000000
  for: 5m
  annotations:
    summary: "Service using >500MB memory"
```

## Disaster Recovery

### Backup Strategy
- Configuration: Daily backups, retained 30 days
- Audit logs: Weekly backups, retained 1 year
- Database state: Continuous replication
- Code: Git repository with tags

### Recovery Procedures
1. **Configuration Loss**: Restore from .env backup
2. **Data Loss**: Rebuild from audit logs
3. **Service Crash**: Auto-restart with systemd/Docker
4. **Complete Loss**: Deploy from latest image + restore configs

### RTO/RPO Goals
- **RTO** (Recovery Time Objective): 5 minutes
- **RPO** (Recovery Point Objective): 1 hour

## Cost Optimization

### Resource Allocation
- Use requests for guaranteed resources
- Use limits to prevent runaway processes
- Prefer shared resources in non-production

### Caching Strategy
- Cache health scores for 10 seconds
- Cache node metrics for 5 seconds
- Cache analytics for 30 seconds

### Database Sizing
- History: Keep 1000+ records (24 hours)
- Events: Keep 1000 events (recent)
- Cleanup: Archive old data weekly

## Compliance & Auditing

### Audit Requirements
- Track all node modifications (taint, drain, remove)
- Log all risk detections with context
- Maintain API access logs
- Preserve action justifications

### Relevant Standards
- SOC 2 Type II
- ISO 27001
- GDPR (if applicable)
- HIPAA (if applicable)

### Audit Log Fields
```python
{
    'timestamp': '2024-02-17T10:30:00Z',
    'action': 'TAINT_NODE',
    'actor': 'ml_engine',
    'resource': 'node-id',
    'reason': 'Risk score 85.3%',
    'status': 'success',
    'changes': {...}
}
```

## Maintenance Windows

### Daily
- Review error logs
- Check health scores
- Verify monitoring active

### Weekly
- Update ML model
- Archive old events
- Review performance metrics
- Security patch scan

### Monthly
- Full system backup
- Capacity analysis
- Performance optimization
- Documentation review

### Quarterly
- Security audit
- Disaster recovery drill
- Cost analysis
- Architecture review

---

**Last Updated**: February 17, 2026
**Version**: 1.0
**Maintained By**: DevOps & Platform Team
