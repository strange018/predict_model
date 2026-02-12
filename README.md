# Predictive Infrastructure Intelligence System

An AI/ML-driven system that proactively prevents infrastructure performance degradation before users are affected. The system continuously monitors node health and uses predictive models to detect risks, automatically migrating workloads from at-risk nodes via Kubernetes native mechanisms (taints, labels).

## 🎯 Key Features

- **Predictive Analytics**: ML-based degradation detection using Gradient Boosting
- **Autonomous Operations**: No manual intervention or scheduler modification required
- **Kubernetes Native**: Uses taints, labels, and evictions to manage workloads
- **Real-time Monitoring**: Continuous node health assessment
- **Event-Driven UI**: Live updates showing system decisions and reasoning
- **Docker Integrated**: Ready-to-deploy containerized setup
- **Demo Mode**: Runs without Kubernetes cluster for testing

## 📋 Architecture

```
┌─────────────────────────────────────────┐
│        Frontend (HTML/CSS/JS)           │
│    Displays events and node metrics     │
└──────────────┬──────────────────────────┘
               │ HTTP/API
               ↓
┌─────────────────────────────────────────┐
│        Backend (Flask)                  │
├─────────────────────────────────────────┤
│ • Event Management                      │
│ • ML Decision Engine (Gradient Boosting)│
│ • Kubernetes Integration                │
│ • Monitoring Service (Autonomous)       │
└──────────────┬──────────────────────────┘
               │ K8s API
               ↓
   ┌─────────────────────────┐
   │  Kubernetes Cluster     │
   │ • Nodes                 │
   │ • Pods                  │
   │ • Taints/Labels         │
   └─────────────────────────┘
```

## 📦 System Components

### Backend (Python Flask)
- **app.py**: Main Flask application and REST API
- **ml_decision_engine.py**: ML model for degradation prediction
- **kubernetes_manager.py**: Kubernetes API integration
- **event_manager.py**: Event tracking and management

### Frontend (Web)
- **index.html**: UI layout
- **styles.css**: Styling and animations
- **script.js**: Real-time updates from backend API

### Container Setup
- **Dockerfile**: Backend containerization
- **docker-compose.yml**: Multi-container orchestration
- **nginx.conf**: Frontend reverse proxy
- **kubernetes-manifest.yaml**: K8s deployment manifests

## 🚀 Quick Start

### Option 1: Local Development (No Kubernetes Required)

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py

# Open frontend in browser
http://localhost:5000
```

The backend will detect that Kubernetes is unavailable and run in **Demo Mode** with simulated metrics.

### Option 2: Docker Compose (Recommended for Testing)

```bash
# Build and start containers
docker-compose up --build

# Access frontend
http://localhost
```

Containers run with demo data by default.

### Option 3: Kubernetes Deployment

```bash
# Prerequisites: Access to running Kubernetes cluster

# Build backend image
docker build -t predictive-infrastructure:latest .

# Push to registry if needed
docker tag predictive-infrastructure:latest <registry>/predictive-infrastructure:latest
docker push <registry>/predictive-infrastructure:latest

# Deploy to cluster
kubectl apply -f kubernetes-manifest.yaml

# Access via service
kubectl port-forward -n predictive-infra svc/predictive-frontend 8000:80
# Visit http://localhost:8000
```

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - System health check
- `GET /api/stats` - System statistics

### Monitoring Control
- `POST /api/monitoring/start` - Start monitoring service
- `POST /api/monitoring/stop` - Stop monitoring service

### Data Retrieval
- `GET /api/nodes` - List all nodes with metrics
- `GET /api/nodes/<node_id>` - Get specific node details
- `GET /api/events` - Get all events
- `GET /api/predictions` - Get ML predictions for all nodes
- `GET /api/ml-insights` - ML model information

### Real-time Streaming
- `GET /api/events/stream` - Server-Sent Events stream for real-time updates

## 🤖 ML Decision Logic

The system uses **Gradient Boosting** to predict node degradation:

### Features Analyzed
1. **CPU Usage** - Processor utilization percentage
2. **Memory Usage** - RAM utilization percentage
3. **Temperature** - Node operating temperature
4. **Network Latency** - Response time on network connections
5. **Disk I/O** - Disk input/output operations
6. **Pod Count** - Number of containers on node

### Risk Scoring
- Risk Score > 0.65 → At Risk (initiate mitigation)
- Risk Score: 0.5-0.65 → Caution (monitor closely)
- Risk Score < 0.5 → Healthy

### Automatic Actions

When risk is detected:

1. **Taint Node**: `degradation=true:NoSchedule` prevents new pods
2. **Drain Workloads**: Gracefully evict running pods with 30s grace period
3. **Migrate**: Move pods to healthy target node with minimum load
4. **Monitor Recovery**: Track metrics as node stabilizes

## 📊 Example Event Flow

```
Timeline: Node degradation detection and mitigation

T+0s   [INFO] Health check passed on worker-01
T+3s   [INFO] Metric update: CPU 45%, Memory 52%
T+6s   [RISK] Risk Detected on worker-02 (Score: 0.78)
       - High CPU (82%)
       - Memory Pressure (88%)
       - Network Latency (35ms)

T+7.5s [ACTION] Node Tainted - Applied degradation=true:NoSchedule
T+8s   [ACTION] Workloads Migrated - Moved 4 pods from worker-02 to worker-01
       - gracePeriod: 30s
       - migrationTime: 25ms

T+9s   [INFO] Node Recovering - Monitoring worker-02 metrics
T+15s  [INFO] Worker-02 metrics back to normal
       - CPU: 35%
       - Memory: 48%
```

## 🔧 Configuration

### ML Model Settings
Edit `ml_decision_engine.py`:
```python
self.risk_threshold = 0.65  # Adjust sensitivity
self.feature_names = [...]  # Modify features
```

### Monitoring Interval
Edit `app.py`:
```python
self.interval = 3  # Monitor every 3 seconds
```

### Kubernetes Settings
Edit `kubernetes_manager.py`:
```python
grace_period = 30  # Pod eviction grace period in seconds
```

## 📝 Environment Variables

```bash
FLASK_ENV=production      # Or 'development'
PYTHONUNBUFFERED=1        # Flush Python output immediately
```

## 🔐 Security Notes

- Backend runs as non-root user (UID 1000)
- Read-only root filesystem in Kubernetes
- RBAC configured for minimal permissions
- HTTPS recommended for production (add nginx SSL config)

## 🧪 Testing the System

### Manual Event Trigger (Demo Mode)

Backend automatically generates events in demo mode. To test with real Kubernetes:

1. Deploy to cluster running `kubernetes-manifest.yaml`
2. Generate load on nodes to trigger degradation detection
3. Watch real-time event feed on frontend

### Metrics Simulation

In demo mode, metrics are randomized. To test specific scenarios, modify `MonitoringService._generate_demo_metrics()` in `app.py`.

## 📈 Performance

- **Latency**: ~50-100ms for event propagation
- **Scalability**: Tested with 5 nodes, easily scales to 50+
- **Resource Usage**: 
  - Backend: 250m CPU, 256Mi Memory (requests)
  - Frontend: 100m CPU, 128Mi Memory (requests)

## 🐛 Troubleshooting

### Backend Won't Connect to Kubernetes
```bash
# Check kubeconfig
export KUBECONFIG=~/.kube/config
kubectl get nodes

# Backend will fall back to demo mode if connection fails
```

### Docker Compose Fails
```bash
# Check docker daemon
docker ps

# Build without cache
docker-compose down -v
docker-compose up --build --no-cache
```

### No Events Appearing
```bash
# Check backend is running
curl http://localhost:5000/api/health

# Verify monitoring started
curl -X POST http://localhost:5000/api/monitoring/start
```

## 📚 Additional Resources

- **Kubernetes Taints & Tolerations**: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
- **Scikit-learn Gradient Boosting**: https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
- **Flask Documentation**: https://flask.palletsprojects.com/

## 🎓 Key Concepts

### Why Predictive?
Traditional monitoring reacts to problems after they occur. This system predicts degradation before users are affected, enabling proactive mitigation.

### Why Autonomous?
No manual intervention required. The system makes decisions based on ML predictions and acts directly on the Kubernetes cluster using native APIs.

### Why Kubernetes Native?
- Uses standard Kubernetes mechanisms (taints, labels, evictions)
- Compatible with all schedulers and workloads
- No application code changes needed
- No scheduler modifications required

## 📄 License

Hackathon Project - Educational Use

## 👥 Contributors

Built for infrastructure reliability and operational excellence.
