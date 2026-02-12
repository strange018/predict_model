# System Integration Guide

## 🏗️ Complete Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Web UI)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Real-time event log with filtering                    │  │
│  │ • Node health metrics (CPU, Memory, Temp, Latency)     │  │
│  │ • Statistics counter (risks, workloads moved)          │  │
│  │ • Auto-refresh every 1.5-3 seconds                     │  │
│  │ Built with: HTML5 + CSS3 + Vanilla JavaScript          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND API (Flask)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Core Routes:                                            │  │
│  │ • GET  /api/health          → {status: healthy}        │  │
│  │ • GET  /api/stats           → {risks, workloads, etc}  │  │
│  │ • GET  /api/nodes           → [{node metrics}]         │  │
│  │ • GET  /api/events          → [{event logs}]           │  │
│  │ • POST /api/predict         → {isRisk, factors}        │  │
│  │ • POST /api/execute-action  → {success}                │  │
│  │ • POST /monitoring/start    → start autonomous mode    │  │
│  │ • POST /monitoring/stop     → stop autonomous mode     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────── Monitoring Service ──────────────────────┐  │
│  │ • Runs in background thread (daemon)                    │  │
│  │ • Collects metrics every 3 seconds                      │  │
│  │ • Calls ML engine for predictions                       │  │
│  │ • Executes K8s actions when needed                      │  │
│  │ • Records events with timestamps                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────┬──────────────────┘
             │                                  │
             ↓                                  ↓
    ┌────────────────┐            ┌────────────────────────┐
    │ ML Engine      │            │ K8s Integration        │
    │ ──────────────│            │ ──────────────────────│
    │• Gradient     │            │ • Node monitoring     │
    │  Boosting     │            │ • Taint application   │
    │• 5 inputs:    │            │ • Pod eviction        │
    │  - CPU        │            │ • Label management    │
    │  - Memory     │            │ • Drain operations    │
    │  - Temp       │            │ • Works in demo mode  │
    │  - Latency    │            │ • Real K8s via API    │
    │  - Disk I/O   │            └────────────────────────┘
    │• Risk score   │
    │  0.0 - 1.0    │
    └────────────────┘
             ↓
    ┌────────────────┐
    │ Event Manager  │
    │ ──────────────│
    │ • In-memory   │
    │   storage     │
    │ • Last 100    │
    │   events      │
    │ • Timestamps  │
    │ • JSON format │
    └────────────────┘
```

---

## 🔄 Data Flow

### **Normal Operation Cycle (Every 3 Seconds)**

```
1. Monitoring Service Awakens
   └─→ Check: Is it time to run? (Yes, 3s passed)

2. Collect Metrics
   ├─→ Real K8s? Query Kubernetes API
   └─→ Demo mode? Generate realistic synthetic metrics

3. Process Each Node
   ├─→ Call ML Engine with metrics
   ├─→ Get prediction: {isRisk: bool, score: 0-1, factors: []}
   └─→ Create event: "Metrics checked - all good"

4. Risk Detection
   └─→ If isRisk == True:
       ├─→ Event: "Risk Detected!"
       ├─→ Log risk factors
       └─→ Schedule action in 1.5 seconds

5. Execute Action (if risk)
   ├─→ Event: "Node Tainted"
   │   └─→ Apply: degradation=true:NoSchedule
   ├─→ Event: "Workloads Migrated"
   │   └─→ Drain pods with 30s grace period
   │   └─→ Move to healthy node
   └─→ Event: "Recovery Monitoring"
       └─→ Watch metrics improve

6. Frontend Update
   ├─→ /api/stats    → Updated counters
   ├─→ /api/events   → New events
   ├─→ /api/nodes    → Updated metrics
   └─→ Browser auto-refresh shows changes
```

---

## 🎯 Integration Components

### **ML Decision Engine** (`ml_decision_engine.py`)

```python
class MLDecisionEngine:
    def __init__(self):
        # Load pre-trained Gradient Boosting model
        self.model = GradientBoostingClassifier(...)
        self.scaler = StandardScaler()
    
    def predict_degradation(self, metrics: dict) -> dict:
        # Input: {cpu, memory, temperature, network_latency, disk_io}
        
        # 1. Scale inputs (normalize to 0-1)
        scaled = self.scaler.transform([metrics])
        
        # 2. Run through ML model
        risk_probability = self.model.predict_proba(scaled)
        
        # 3. Determine if risky
        is_risk = risk_probability[1] > THRESHOLD  # 0.65
        
        # 4. Identify factors
        factors = self._identify_risk_factors(metrics)
        
        # 5. Return prediction
        return {
            'isRisk': is_risk,
            'riskScore': float(risk_probability[1]),
            'factors': factors
        }
```

**Input Metrics:**
- CPU usage: 0-100%
- Memory usage: 0-100%
- Temperature: 40-90°C
- Network latency: 1-50ms
- Disk I/O: 0-100%

**Output:**
- `isRisk`: Boolean (True = degradation likely)
- `riskScore`: Float 0.0-1.0 (confidence)
- `factors`: List of detected issues

---

### **Kubernetes Integration** (`kubernetes_manager.py`)

```python
class KubernetesManager:
    def __init__(self):
        # Load kubeconfig or use in-cluster authentication
        config.load_incluster_config()  # or load_kube_config()
        self.v1 = client.CoreV1Api()
        
    def get_nodes(self):
        """Get all nodes in cluster"""
        nodes = self.v1.list_node()
        return [node.metadata.name for node in nodes.items]
    
    def taint_node(self, node_name: str, taint: str):
        """Apply taint to prevent new pods"""
        # Example: "degradation=true:NoSchedule"
        patch = {
            "spec": {
                "taints": [{"key": "degradation", "value": "true", "effect": "NoSchedule"}]
            }
        }
        self.v1.patch_node(node_name, patch)
    
    def drain_node(self, node_name: str, grace_period: int = 30):
        """Gracefully evict pods from node"""
        # 1. Get all pods on node
        pods = self.v1.list_namespaced_pod(
            namespace="", 
            field_selector=f"spec.nodeName={node_name}"
        )
        
        # 2. Evict each pod with grace period
        for pod in pods.items:
            self.v1.delete_namespaced_pod(
                pod.metadata.name,
                pod.metadata.namespace,
                grace_period_seconds=grace_period
            )
```

**Actions:**
1. **Taint Node**: Prevent new pods from being scheduled
2. **Drain Node**: Gracefully evict existing pods
3. **Remove Taint**: Allow scheduling again (recovery)
4. **Relabel Node**: Add/remove labels for workload affinity

---

### **Event Management** (`event_manager.py`)

```python
class EventManager:
    def __init__(self):
        self.events = deque(maxlen=100)  # Keep last 100 events
    
    def add_event(self, event: dict):
        """Record an event"""
        event['id'] = len(self.events)
        event['timestamp'] = datetime.now().isoformat()
        self.events.appendleft(event)  # Newest first
    
    def get_events(self, event_type=None, limit=50):
        """Retrieve events with optional filtering"""
        events = list(self.events)
        
        if event_type:
            events = [e for e in events if e.get('type') == event_type]
        
        return events[:limit]
```

**Event Types:**
- `risk` - Degradation detected
- `action` - Kubernetes action taken
- `info` - Status updates

---

## 📡 API Contract

### **Request/Response Examples**

**GET /api/health**
```json
Response 200:
{
  "status": "healthy",
  "timestamp": "2026-02-10T12:34:56.789Z",
  "services": {
    "ml_engine": "ready",
    "kubernetes": "connected",  // or "demo_mode"
    "monitoring": "running"
  }
}
```

**GET /api/stats**
```json
Response 200:
{
  "nodes_monitored": 5,
  "risks_detected": 3,
  "workloads_moved": 8,
  "monitoring_uptime": 3600,  // seconds
  "events_total": 42
}
```

**GET /api/nodes**
```json
Response 200:
[
  {
    "node_id": "node-01",
    "name": "worker-01",
    "status": "healthy",
    "metrics": {
      "cpu": 45.2,
      "memory": 62.1,
      "temperature": 58.5,
      "network_latency": 4.2,
      "disk_io": 23.4
    }
  },
  {
    "node_id": "node-02",
    "name": "worker-02",
    "status": "at-risk",
    "metrics": { ... }
  }
]
```

**POST /api/predict**
```json
Request Body:
{
  "metrics": {
    "cpu": 87.3,
    "memory": 89.1,
    "temperature": 76.5,
    "network_latency": 32.4,
    "disk_io": 78.9
  }
}

Response 200:
{
  "prediction": {
    "isRisk": true,
    "riskScore": 0.78,
    "factors": [
      "High CPU utilization",
      "Memory pressure increasing",
      "Temperature threshold exceeded"
    ]
  }
}
```

---

## 🔌 Frontend Integration

### **API Polling Pattern**

```javascript
// Frontend refreshes data from backend every N seconds

// Every 2 seconds: Update statistics
setInterval(() => {
  fetch('/api/stats')
    .then(r => r.json())
    .then(data => updateDashboard(data))
}, 2000);

// Every 3 seconds: Update node metrics
setInterval(() => {
  fetch('/api/nodes')
    .then(r => r.json())
    .then(nodes => renderNodeCards(nodes))
}, 3000);

// Every 1.5 seconds: Update events
setInterval(() => {
  fetch('/api/events')
    .then(r => r.json())
    .then(events => appendNewEvents(events))
}, 1500);
```

### **Event Filtering**

```javascript
// Filter events by type
const filteredEvents = events.filter(e => e.type === 'risk');

// Display with color coding
event.risk    → Red border, ⚠️ icon
event.action  → Green border, ✓ icon
event.info    → Blue border, ℹ️ icon
```

---

## 🐳 Deployment Modes

### **1. Demo Mode (No K8s Required)**
```python
# app.py detects K8s unavailable
try:
    k8s_manager = KubernetesManager()
except:
    k8s_manager = None  # Use demo metrics
    print("Running in DEMO MODE")

# Use synthetic metrics instead
def generate_demo_metrics():
    return {
        'cpu': random(20, 90),
        'memory': random(30, 85),
        'temperature': random(45, 80),
        ...
    }
```

### **2. Docker Compose Mode**
```yaml
services:
  backend:
    build: .
    ports: ["5000:5000"]
    volumes:
      - ~/.kube/config:/app/.kube/config  # K8s access
  
  frontend:
    image: nginx:alpine
    ports: ["80:80"]
    depends_on:
      - backend
```

### **3. Kubernetes Native**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: predictive-backend
  namespace: predictive-infra
spec:
  containers:
  - name: backend
    image: predictive-infrastructure:latest
    env:
    - name: KUBERNETES_SERVICE_HOST
      value: kubernetes.default.svc
    serviceAccountName: predictive-backend
```

---

## 🧪 Testing the Integration

### **1. Verify All Dependencies**
```bash
python verify.py
# Output: Summary of all component tests
```

### **2. Test ML Predictions**
```python
from ml_decision_engine import MLDecisionEngine

engine = MLDecisionEngine()
metrics = {'cpu': 85, 'memory': 88, ...}
result = engine.predict_degradation(metrics)
print(result)  # {isRisk: True, riskScore: 0.78, ...}
```

### **3. Test API Endpoints**
```bash
# In Python
python -c "
from app import app
client = app.test_client()
print(client.get('/api/health').json)
print(client.get('/api/stats').json)
"

# In terminal
curl http://localhost:5000/api/health
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/nodes
```

### **4. Test Monitoring Service**
```bash
# Start backend
python app.py

# In another terminal, watch events
while true; do
  curl http://localhost:5000/api/events | jq '.[0]'
  sleep 2
done
```

---

## 📊 Performance Metrics

### **System Overhead**
- **CPU per cycle**: ~50ms (3-second interval)
- **Memory footprint**: ~150MB (with all libraries)
- **Event buffer**: 100 items (manageable in memory)
- **API response time**: <50ms

### **Kubernetes Operations**
- **Taint application**: <100ms
- **Pod eviction**: <500ms (+ grace period)
- **Node drain**: 30s (hard-coded grace period)
- **API calls**: Batched when possible

---

## 🔒 Security Considerations

### **Current Design (Demo)**
- No authentication on API
- All endpoints accessible
- Kubeconfig mounted with full permissions

### **Production Hardening**
1. Add JWT authentication
2. Implement RBAC for API endpoints
3. Use read-only role for Kubernetes
4. Lock down to specific namespaces
5. Enable HTTPS/TLS
6. Add rate limiting
7. Implement audit logging

---

## 🚀 Ready to Launch!

All components are integrated and tested:
- ✅ Frontend displays real-time updates
- ✅ Backend API serves metrics and events
- ✅ ML engine makes predictions
- ✅ Kubernetes manager applies actions
- ✅ Demo mode works without cluster
- ✅ Docker ready for containerization

**Start the system:**
```bash
python app.py
# Then open: http://localhost:5000
```
