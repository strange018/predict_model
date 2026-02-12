# 🚀 Quick Start Guide

## System Overview

The **Predictive Infrastructure Intelligence System** is a fully integrated solution with:

- **Frontend**: Real-time web UI showing node health and autonomous decisions
- **Backend**: Flask API with ML-powered prediction engine
- **Kubernetes Integration**: Native node taints/labels for workload management
- **Docker Support**: Containerized deployment option
- **Demo Mode**: Runs without requiring Kubernetes cluster

---

## 🎯 Choose Your Launch Method

### **Option 1: Local Demo (Windows) ⭐ RECOMMENDED FOR TESTING**

Fastest way to see the system in action with simulated Kubernetes environment.

**Windows (PowerShell):**
```powershell
cd "c:\Users\HP\OneDrive\Desktop\hackathon project"
python app.py
```

**Windows (Command Prompt):**
```batch
cd c:\Users\HP\OneDrive\Desktop\hackathon project
start.bat
```

Then open browser: **http://localhost:5000**

### **Option 2: Docker Compose**

Containerized setup with frontend, backend, and optional MongoDB.

```bash
cd "/Users/HP/OneDrive/Desktop/hackathon project"
docker-compose up --build
```

Access: **http://localhost**

### **Option 3: Kubernetes Deployment**

Deploy to actual Kubernetes cluster with real monitoring.

```bash
# Apply manifests to cluster
kubectl apply -f kubernetes-manifest.yaml

# Monitor deployment
kubectl get pods -n predictive-infra
kubectl logs -n predictive-infra -l app=predictive-backend -f
```

---

## 📊 What You'll See

After starting, the system will:

1. **Initialize** the Flask backend API
2. **Start monitoring** 5 simulated Kubernetes nodes
3. **Simulate workloads** and generate realistic metrics
4. **Detect risks** when metrics exceed thresholds:
   - CPU > 80%
   - Memory > 85%
   - Temperature > 75°C
   - Network Latency > 30ms

5. **Automatically respond** by:
   - Tainting the at-risk node
   - Moving workloads to healthy nodes
   - Tracking recovery

---

## 🎮 Demo Sequence (What Happens)

The system runs autonomously every 3 seconds:

```
Cycle 1-5: ✓ Normal operations
├─ Monitor nodes: CPU 45%, Memory 55%, Temp 58°C
└─ Status: All healthy

Cycle 6: ⚠️ Risk detected!
├─ Node worker-02 CPU jumped to 86%
├─ ML Engine: RISK SCORE = 0.78 (HIGH)
└─ Event: "Risk Detected - Performance degradation predicted"

Cycle 7: 🔄 Action taken
├─ Applied taint: degradation=true:NoSchedule
├─ Drained 3 pods from worker-02
├─ Moved pods to worker-01 (available capacity)
└─ Event: "Moved 3 workloads from worker-02 to worker-01"

Cycle 8+: 📈 Recovery monitoring
├─ Node stabilizing: CPU 72% → 58% → 42%
├─ Remove taint when safe
└─ Event: "Node recovered - back to normal"
```

---

## 📱 UI Dashboard

The web interface displays 4 sections:

### **1. Statistics Bar**
- Nodes Being Monitored: 5
- Risks Detected: Counter
- Workloads Moved: Counter
- Last Update: Time

### **2. Event Log** 
Real-time feed with color-coded events:
- 🔴 **Risk** events (red) - degradation detected
- 🟢 **Action** events (green) - workloads moved
- 🔵 **Info** events (blue) - status updates

Filter by type:
- All / Risk / Action / Info

### **3. Node Health Metrics**
Individual cards for each node showing:
- CPU usage (0-100%)
- Memory usage (0-100%)
- Temperature (40-90°C)
- Network latency (1-50ms)
- Disk I/O (0-100%)

Color coding:
- 🟢 Green: Healthy
- 🟡 Yellow: Warning (> 70%)
- 🔴 Red: Critical (> 85%)

### **4. Header**
- System status (Monitoring Active)
- Real-time sync indicator

---

## 🔌 API Endpoints

When backend is running, access these endpoints:

```
GET  http://localhost:5000/api/health
     → Returns { status: "healthy" }

GET  http://localhost:5000/api/stats
     → Returns { nodes_monitored, risks_detected, workloads_moved }

GET  http://localhost:5000/api/nodes
     → Returns [ { node_id, metrics }, ... ]

GET  http://localhost:5000/api/events
     → Returns [ { type, title, description, timestamp }, ... ]

POST http://localhost:5000/api/predict
     → Input: { metrics }
     → Returns: { isRisk: bool, factors: [], riskScore: 0.0-1.0 }

POST http://localhost:5000/api/execute-action
     → Input: { action_type, target_node, details }
     → Returns: { success: bool, message: string }

POST http://localhost:5000/monitoring/start
     → Starts autonomous monitoring service

POST http://localhost:5000/monitoring/stop
     → Stops autonomous monitoring service
```

---

## 🛠️ Monitoring Service Details

The backend includes an autonomous monitoring service that:

1. **Every 3 seconds**:
   - Collects metrics from Kubernetes nodes
   - In demo mode: Generates realistic simulated metrics

2. **For each node**:
   - Runs ML prediction model (Gradient Boosting)
   - Checks if degradation is likely

3. **If risk detected**:
   - Creates "Risk Detected" event
   - Automatically applies taints
   - Drains pods gracefully (30-second grace period)
   - Moves workloads to healthy nodes

4. **Logs everything**:
   - Events stored in memory (last 100)
   - Timestamps and reasoning included
   - Front-end updated in real-time

---

## 🧠 ML Decision Engine

The ML model uses **Gradient Boosting** and considers:

- **CPU usage trend**: 0-100%, weighted heavily
- **Memory pressure**: 0-100%, gradient important
- **Temperature**: 40-90°C scale
- **Network latency**: 1-50ms, spike detection
- **Disk I/O**: 0-100%, I/O bottleneck risk

**Risk Thresholds**:
- Score < 0.4: ✓ Healthy
- Score 0.4-0.65: ⚠️ Monitor closely
- Score > 0.65: 🔴 Action triggered

---

## 📋 Configuration

### **Monitoring Interval**
In `app.py`, line ~60:
```python
self.interval = 3  # seconds between checks
```

### **Risk Threshold**
In `ml_decision_engine.py`:
```python
RISK_THRESHOLD = 0.65  # 0-1 scale
```

### **ML Model Retraining**
Every 24 hours in production mode
Can be configured in `kubernetes-manifest.yaml` ConfigMap

---

## 🐛 Troubleshooting

### **Backend won't start**
```powershell
# Check Python version
python --version

# Check dependencies
pip install -r requirements.txt

# Run in verbose mode
python -u app.py
```

### **Kubernetes connection error**
This is expected in demo mode. To use real Kubernetes:
- Set `KUBECONFIG` environment variable
- Ensure `kubectl` can access your cluster

### **Frontend not updating**
- Browser console (F12) should show API calls
- Check backend is running: http://localhost:5000/api/health
- Clear browser cache (Ctrl+Shift+Delete)

### **Node metrics not showing**
- Backend is in demo mode (expected)
- Wait 5-10 seconds for initial data
- Check browser console for errors

---

## 📦 Files Structure

```
hackathon project/
├── app.py                    # Main Flask backend
├── ml_decision_engine.py     # Gradient Boosting model
├── kubernetes_manager.py     # K8s API integration
├── event_manager.py          # Event tracking
├── index.html                # Frontend UI
├── styles.css                # Styling
├── script.js                 # Frontend logic
├── Dockerfile                # Container build
├── docker-compose.yml        # Multi-container setup
├── kubernetes-manifest.yaml  # K8s deployment
├── requirements.txt          # Python dependencies
├── start.bat                 # Windows launch
├── launch.sh                 # Linux/Mac launch
└── QUICKSTART.md            # This file
```

---

## 💡 Tips & Tricks

1. **See backend logs**: The console shows all risk detections and actions
2. **Watch specific node**: Filter by node name in frontend (planned feature)
3. **Pause monitoring**: API endpoint to stop autonomous mode
4. **Replay events**: Load historical events from database (with DB)
5. **Custom thresholds**: Pass via environment variables

---

## 🎓 For Developers

### Testing the ML Model
```python
from ml_decision_engine import MLDecisionEngine

engine = MLDecisionEngine()
metrics = {
    'cpu': 85,
    'memory': 88,
    'temperature': 72,
    'network_latency': 25,
    'disk_io': 45
}
prediction = engine.predict_degradation(metrics)
print(prediction)  # { 'isRisk': True, 'factors': [...], 'riskScore': 0.78 }
```

### Testing Kubernetes Operations
```python
from kubernetes_manager import KubernetesManager

k8s = KubernetesManager()
nodes = k8s.get_nodes()
k8s.taint_node('worker-02', 'degradation=true:NoSchedule')
k8s.drain_node('worker-02')
```

### Adding Custom Metrics
Edit `ml_decision_engine.py` `predict_degradation()` method to include:
- Custom thresholds
- New data sources
- Different algorithms

---

## 📞 Support

### Common Commands

**Stop the system**:
- Press `Ctrl+C` in terminal

**View real-time logs**:
- Check the terminal output
- Browser console: F12 → Console tab

**Check system health**:
- GET http://localhost:5000/api/health

**Clear event history**:
- Restart the application

---

## 🚀 Next Steps

After running in demo mode, you can:

1. **Test with Docker**: `docker-compose up`
2. **Deploy to Kubernetes**: `kubectl apply -f kubernetes-manifest.yaml`
3. **Customize thresholds**: Edit config in `kubernetes-manifest.yaml`
4. **Add persistence**: Configure MongoDB in `docker-compose.yml`
5. **Build UI extensions**: Modify `script.js` for custom dashboards

---

**Enjoy the Predictive Infrastructure Intelligence System! 🎯**
