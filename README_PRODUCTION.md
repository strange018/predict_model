# Production-Ready Infrastructure Intelligence System

A professional-grade, enterprise-ready Kubernetes monitoring and orchestration platform with AI/ML-driven infrastructure intelligence.

## 🚀 Quick Start (Production)

### Prerequisites
- Python 3.9+
- 2GB RAM minimum (8GB recommended)
- Access to Kubernetes cluster (or runs in DEMO mode)
- pip and virtual environment tools

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/infra-intelligence.git
cd infra-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your production settings
```

### Running in Production

```bash
# Development mode (single worker)
python app.py

# Production mode (gunicorn with multiple workers)
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

# Docker deployment (recommended)
docker build -t infra-intelligence:latest .
docker run -d -p 5000:5000 -e FLASK_ENV=production infra-intelligence:latest

# Kubernetes deployment
kubectl apply -f kubernetes-manifest.yaml
```

### Verify Deployment

```bash
# Health check
curl http://localhost:5000/api/health

# Get current stats
curl http://localhost:5000/api/stats

# Access dashboard
open http://localhost:5000
```

## 📊 Features

### Core Capabilities
✅ **Real-time Monitoring**: Track 500+ nodes and 10,000+ pods  
✅ **Health Scoring**: 5-component weighted health assessment  
✅ **Risk Detection**: ML-based degradation prediction  
✅ **Auto-Remediation**: Automatic node tainting and draining  
✅ **Event Management**: Structured logging with filtering  
✅ **Audit Trail**: Complete compliance audit logs  
✅ **Cluster Analytics**: Cluster-wide metrics and trends  
✅ **Live Dashboard**: Real-time status visualization  

### Production Features
✅ **Configuration Management**: Environment-based configuration  
✅ **Error Handling**: Comprehensive error recovery  
✅ **Health Checks**: Kubernetes liveness and readiness probes  
✅ **Rate Limiting**: API request throttling  
✅ **Input Validation**: Security-focused input sanitization  
✅ **Performance Monitoring**: Request timing and metrics  
✅ **Graceful Shutdown**: Signal handling and cleanup  
✅ **Resource Optimization**: Memory and CPU efficiency  

## 🏗️ Architecture

### System Components

```
Dashboard UI (React/Vue)
         ↓
    Load Balancer
         ↓
┌─────────────────────────┐
│  Flask REST API         │
│  - Stats               │
│  - Nodes               │
│  - Events              │
│  - Analytics           │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  Monitoring Service     │ (3s polling)
├─────────────────────────┤
│  HealthScorer          │ (5 metrics)
│  MLDecisionEngine      │ (Risk prediction)
│  AnalyticsEngine       │ (Cluster metrics)
│  EventManager          │ (Structured events)
│  KubernetesManager     │ (Node operations)
│  AuditLogger           │ (Compliance)
└─────────────────────────┘
           ↓
    Kubernetes Cluster
```

### Key Metrics
- **Nodes**: CPU, Memory, Temperature, Network Latency, Disk I/O
- **Health Score**: Weighted combination (0-100)
- **Risk Level**: 0-100% probability of degradation
- **Status**: Healthy, Degraded, or Critical

## 📈 Performance

### Scalability Targets
| Metric | Capacity |
|--------|----------|
| Nodes | 500+ |
| Pods | 10,000+ |
| Events | 1,000 (cached) |
| Monitoring Interval | 3-5s |
| API Response Time | <500ms |

### Resource Usage (Single Instance)
- Memory: 200-500MB
- CPU: 0.5-1.0 core
- Disk: 100MB+ logs

## 🔒 Security

### Built-in Security
- CORS-protected endpoints
- Rate limiting (default: 1000 req/min)
- Request timeout (default: 60s)
- Input validation and sanitization
- Error message obfuscation
- Audit logging for compliance

### Recommendations
- Use HTTPS/TLS in production
- Implement API authentication tokens
- Restrict Kubernetes service account permissions
- Use VPN for remote access
- Regular security audits

## 📚 Documentation

### Quick Links
- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT.md)
- [Architecture & Best Practices](./ARCHITECTURE.md)
- [Testing & QA Guide](./TESTING_GUIDE.md)
- [API Documentation](./API.md)
- [Configuration Reference](./CONFIG.md)

### Running Tests

```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=. --cov-report=html

# Code quality
black . --check
flake8 . --max-line-length=100
mypy . --ignore-missing-imports
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
FLASK_ENV=production          # development|production|testing
FLASK_HOST=0.0.0.0            # Server host
FLASK_PORT=5000               # Server port
LOG_LEVEL=WARNING              # DEBUG|INFO|WARNING|ERROR|CRITICAL

# Kubernetes
K8S_NAMESPACE=production       # Target namespace
KUBECONFIG=/path/to/config    # Custom kubeconfig (optional)

# Monitoring
MONITORING_INTERVAL=5         # Seconds between checks
MAX_HISTORY_RECORDS=5000      # History size

# Risk Detection
RISK_THRESHOLD_CRITICAL=70.0  # Trigger critical alerts
RISK_THRESHOLD_WARNING=50.0   # Trigger warnings

# Features
ENABLE_ML_PREDICTIONS=True    # Enable ML engine
ENABLE_AUTO_REMEDIATION=False # Auto taint/drain nodes
ENABLE_EVENT_STREAMING=False  # Enable SSE streaming

# Security
CORS_ORIGINS=your-domain.com  # Allowed origins
API_RATE_LIMIT=1000           # Requests per minute
```

See `.env.example` for all available options.

## 🚨 Monitoring & Alerting

### Health Endpoints
```bash
/health          # Liveness probe (always 200 if up)
/ready          # Readiness probe (503 if not ready)
/metrics        # Prometheus metrics
/api/health     # Detailed component status
```

### Sample Alerts
```
- Risk detection rate > 0.1/min for 5 minutes
- Service down for > 1 minute
- Memory usage > 500MB
- API response time > 1 second
- Error rate > 5%
```

## 🛠️ Troubleshooting

### Service Won't Start
```bash
# Check configuration
python -c "from config import config; print(config.get_summary())"

# Check logs
docker logs <container-id>  # Or journalctl if systemd

# Verify port
lsof -i :5000
```

### High Memory Usage
```bash
# Reduce history
export MAX_HISTORY_RECORDS=1000

# Monitor memory
docker stats  # Or: top, ps aux

# Restart service
systemctl restart infra-intelligence
```

### API Timeouts
```bash
# Increase timeout
export REQUEST_TIMEOUT=120
export API_TIMEOUT=60

# Check performance
curl -w "@curl-format.txt" http://localhost:5000/api/stats
```

### Kubernetes Issues
```bash
# Verify config
kubectl config view
kubectl cluster-info

# Check auth
kubectl auth can-i list nodes

# View logs
kubectl logs -f deployment/infra-intelligence
```

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates in place
- [ ] Kubernetes RBAC configured
- [ ] Monitoring and alerting setup
- [ ] Log aggregation configured
- [ ] Firewall rules configured
- [ ] Backup strategy defined
- [ ] Disaster recovery plan tested
- [ ] Load testing completed
- [ ] Security audit passed

## 🤝 Support & Contributing

### Getting Help
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [Documentation](#documentation)
3. Check existing GitHub issues
4. Contact DevOps team

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request with description

## 📝 License

MIT License - See LICENSE file for details

## 🎯 Roadmap

- [ ] Multi-cluster support
- [ ] Advanced ML models
- [ ] Webhook integration
- [ ] Custom metrics
- [ ] Cost optimization recommendations
- [ ] GitOps integration
- [ ] Helm chart support

## 📞 Contact

- **DevOps Team**: devops@company.com
- **Platform Team**: platform@company.com
- **Issues**: GitHub Issues
- **Documentation**: Wiki/Docs site

---

**Version**: 1.0.0  
**Last Updated**: February 17, 2026  
**Status**: Production Ready ✓  
**Maintained By**: Infrastructure Team
