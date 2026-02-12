## 📑 DOCUMENTATION INDEX

Complete guide to all files and documentation for the Predictive Infrastructure Monitoring system.

---

## 🎯 START HERE

### 1. **[STATUS.md](STATUS.md)** ⭐ READ THIS FIRST
   - Summary of what was fixed
   - Quick verification steps
   - Architecture overview
   - Latest improvements

### 2. **[QUICK_START.md](QUICK_START.md)** 
   - Step-by-step verification that UI updates are working
   - How to test button clicks
   - What to look for in the console
   - Troubleshooting tips

---

## 🔧 SETUP & DEPLOYMENT

### 3. **[CLUSTER_SETUP.md](CLUSTER_SETUP.md)**
   - How to connect to real Kubernetes cluster
   - Minikube setup instructions
   - Cloud provider (AWS, GKE, Azure) options
   - KUBECONFIG setup

### 4. **[CLUSTER_INTEGRATION.md](CLUSTER_INTEGRATION.md)**
   - Detailed Kubernetes integration guide
   - API configuration for different K8s versions
   - Security considerations
   - Scaling recommendations

### 5. **[GETTING_STARTED.md](GETTING_STARTED.md)**
   - Project overview
   - System architecture
   - Feature list
   - Local development setup

---

## 🐛 DEBUGGING & TESTING

### 6. **[DEBUG_GUIDE.md](DEBUG_GUIDE.md)**
   - Detailed troubleshooting for "not updating" issues
   - Browser console debugging steps
   - Backend verification
   - Common issues and fixes

### 7. **[test_ui_updates.py](test_ui_updates.py)**
   - Python script to test API endpoints without browser
   - Tests taint, remove-taint, drain actions
   - Verifies backend is responding correctly
   - Usage: `python test_ui_updates.py`

### 8. **[/console-monitor](http://127.0.0.1:5000/console-monitor)**
   - Live browser-based console viewer
   - Real-time log display with color coding
   - Test buttons within the console
   - Easy debugging without DevTools

---

## 📚 API REFERENCE

### 9. **[API.md](API.md)**
   - Complete REST API endpoint documentation
   - Request/response examples
   - Error codes and meanings
   - Authentication (if applicable)

---

## 💾 MAIN SOURCE FILES

### 10. **[app.py](app.py)** (Backend - 630+ lines)
Primary Flask application with:
- REST API endpoints (/api/nodes, /api/events, etc.)
- Background monitoring service
- ML decision engine integration
- Kubernetes client wrapper
- Demo mode for testing without cluster
- Static file serving

**Key endpoints:**
- `GET /api/health` - System status
- `GET /api/nodes` - List all nodes
- `POST /api/nodes/<id>/taint` - Apply taint
- `POST /api/nodes/<id>/remove-taint` - Remove taint
- `POST /api/nodes/<id>/drain` - Drain node
- `GET /api/events` - List recent events
- `GET /api/stats` - System statistics

### 11. **[script.js](script.js)** (Frontend - 540+ lines)
JavaScript monitoring interface with:
- Polling service (stats, nodes, events)
- Real-time UI updates
- Interactive buttons
- Event feed
- Server-sent events support
- Comprehensive console logging

**Key components:**
- `InfrastructureMonitor` class - Main orchestrator
- `fetchNodes()` - Poll node status
- `renderNodeMetrics()` - Display node cards
- `applyTaint()`, `removeTaint()`, `drainNode()` - Button handlers

### 12. **[index.html](index.html)** (Frontend - 78 lines)
Main HTML interface with:
- Header with status indicators
- Stats section (risks, workloads)
- Node grid display
- Event feed
- Responsive layout

### 13. **[styles.css](styles.css)** (Styling - 500+ lines)
Modern dark theme with:
- Node card styling
- Status indicators
- Metric bars with colors
- Taint badges
- Event animations
- Responsive grid layout

---

## 🤖 ML & KUBERNETES INTEGRATION

### 14. **[ml_decision_engine.py](ml_decision_engine.py)**
Machine learning models for:
- Node degradation prediction
- Risk scoring
- Feature importance analysis
- Uses scikit-learn Gradient Boosting (87% accuracy)

**Key methods:**
- `predict_degradation()` - Predict if node will fail
- `get_feature_importance()` - Which metrics matter most
- `get_model_accuracy()` - Model performance metrics

### 15. **[kubernetes_manager.py](kubernetes_manager.py)** (295 lines)
Kubernetes API wrapper supporting:
- In-cluster authentication
- KUBECONFIG file loading
- Node metrics collection
- Taint operations
- Workload draining
- Pod eviction handling

**Key methods:**
- `get_nodes_metrics()` - Fetch CPU, memory, etc.
- `taint_node()` - Add scheduler prevention
- `drain_node()` - Evict all pods from node
- `remove_taint()` - Remove scheduler prevention

### 16. **[event_manager.py](event_manager.py)** (150+ lines)
Event logging and tracking:
- Deque-based event storage (last 200 events)
- UUID-based event tracking
- Event filtering by type (risk/action/info)
- Statistics generation

**Key methods:**
- `add_event()` - Log new event
- `get_events()` - Retrieve all events
- `get_events_by_node()` - Node-specific events

---

## 🐳 CONTAINERIZATION

### 17. **[Dockerfile](Dockerfile)**
Multi-stage Docker build:
- Python 3.10+ base
- Dependencies installation
- Production-ready configuration
- Usage: `docker build -t infra-monitor .`

### 18. **[docker-compose.yml](docker-compose.yml)**
Local development setup:
- Flask app on port 5000
- Volume mounts for live editing
- Environment configuration
- Usage: `docker-compose up`

### 19. **[kubernetes_manifest.yaml](kubernetes_manifest.yaml)**
Kubernetes deployment configuration:
- Container image specification
- Service definition
- Resource requests/limits
- Health checks

---

## 📋 SETUP HELPERS

### 20. **[setup_minikube.py](setup_minikube.py)**
Automated Minikube setup and validation:
- Check Minikube installation
- Start cluster
- Verify connectivity
- Display kubeconfig path

### 21. **[validate_cluster.py](validate_cluster.py)**
Cluster connectivity validation:
- Test Kubernetes API access
- Verify node discovery
- Check RBAC permissions
- Validate service account

---

## 📖 GUIDES & DOCUMENTATION

### Additional Files:
- **[FILES_INDEX.md](FILES_INDEX.md)** - File structure overview
- **[CLUSTER_QUICK_START.md](CLUSTER_QUICK_START.md)** - Quick cluster connection guide
- **[TEST_CLUSTER_OPTIONS.md](TEST_CLUSTER_OPTIONS.md)** - Cloud/Minikube/Demo options

---

## 🔄 WORKFLOW GUIDE

### To Verify Everything Works:
1. Read **STATUS.md** (2 min)
2. Run **QUICK_START.md** (5 min)
3. Test with **test_ui_updates.py** (1 min)
4. Open **/console-monitor** and watch logs

### To Deploy to Kubernetes:
1. Follow **CLUSTER_SETUP.md**
2. Run **validate_cluster.py**
3. Update `kubernetes_manager.py` config
4. Deploy with **kubernetes_manifest.yaml**

### To Troubleshoot Issues:
1. Check **DEBUG_GUIDE.md**
2. Use **/console-monitor** live view
3. Run **test_ui_updates.py** for API testing
4. Check **app.py** logs in terminal

---

## 🎮 QUICK COMMANDS

```bash
# Start backend
python app.py

# Test API endpoints
python test_ui_updates.py

# Docker build
docker build -t infra-monitor .

# Docker Compose
docker-compose up

# Validate cluster connection
python validate_cluster.py

# Setup Minikube
python setup_minikube.py
```

---

## 🌐 LOCAL URLS

- **Main UI:** http://127.0.0.1:5000
- **Console Monitor:** http://127.0.0.1:5000/console-monitor
- **API Health:** http://127.0.0.1:5000/api/health
- **API Nodes:** http://127.0.0.1:5000/api/nodes
- **API Events:** http://127.0.0.1:5000/api/events

---

## 💡 KEY FEATURES

✅ **Real-Time Monitoring**
- Live node metrics (CPU, Memory, Temperature, Network, Disk)
- Event logging and streaming
- Status indicators and alerts

✅ **Interactive Controls**
- Taint/Untaint nodes
- Drain workloads
- View event history
- Monitor predictions

✅ **ML Integration**
- Degradation prediction
- Risk scoring
- Feature importance analysis

✅ **Kubernetes Ready**
- Works with any K8s cluster
- In-cluster and kubeconfig authentication
- Demo mode for local testing
- RBAC-aware operations

✅ **Production Ready**
- Docker containerization
- Comprehensive logging
- Health checks
- Error handling

---

## 🚀 NEXT STEPS

1. **Verify** - Run through QUICK_START.md
2. **Test** - Use test_ui_updates.py and /console-monitor
3. **Deploy** - Follow CLUSTER_SETUP.md for your infrastructure
4. **Monitor** - Watch metrics and events in real-time

---

## 📞 SUPPORT

All guides include:
- Step-by-step instructions
- Common issues and fixes
- Troubleshooting flowcharts
- Code examples
- Command references

Check the relevant guide for your specific task!
