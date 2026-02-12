# Predictive Infrastructure Intelligence - Complete Setup Guide

## What You Have

A complete AI-driven Kubernetes infrastructure management system with:

- ✅ **Interactive Web UI** - Real-time node monitoring and control
- ✅ **ML Predictions** - Gradient Boosting model for degradation detection  
- ✅ **Node Actions** - Taint, Drain, Remove Taint operations
- ✅ **Event System** - Live event log with Server-Sent Events
- ✅ **REST API** - Full API for programmatic access
- ✅ **Demo Mode** - Works without a cluster (testing)
- ✅ **Cluster Mode** - Connects to real Kubernetes clusters
- ✅ **Docker Ready** - Dockerfile and docker-compose included
- ✅ **K8s Ready** - Kubernetes manifests for deployment

## Quick Start (Demo Mode - No Cluster Needed)

The system is **already running** in the terminal with demo data:

```bash
# Frontend is accessible at:
http://127.0.0.1:5000

# Try clicking buttons in the UI:
# - Taint: Prevent new pods from scheduling
# - Drain: Evict all pods from node
# - Remove Taint: Restore node to normal state

# All operations are simulated and show in the event log
```

## Connect to Real Kubernetes Cluster

To manage a **real cluster**, follow these steps:

### Step 1: Get Your Kubeconfig

**AWS EKS:**
```bash
aws eks update-kubeconfig --name YOUR_CLUSTER --region YOUR_REGION
```

**Google GKE:**
```bash
gcloud container clusters get-credentials YOUR_CLUSTER --zone YOUR_ZONE
```

**Azure AKS:**
```bash
az aks get-credentials --resource-group YOUR_RG --name YOUR_CLUSTER
```

**Other clusters:** Ask your admin for the `kubeconfig` file

### Step 2: Validate Setup

```bash
# Run validation to check everything is ready
python validate_cluster.py

# Expected output on success:
# ✓ PASS: Kubeconfig
# ✓ PASS: Kubernetes Client
# ✓ PASS: Cluster Connection
# ✓ PASS: RBAC Permissions
```

### Step 3: Connect System to Cluster

**Windows (PowerShell):**
```powershell
# Option A: Set environment variable
$env:KUBECONFIG = "C:\Users\YourName\.kube\config"
python app.py

# Option B: Use setup script
.\setup_cluster.bat "C:\Users\YourName\.kube\config"
```

**Linux/Mac:**
```bash
# Option A: Set environment variable
export KUBECONFIG=~/.kube/config
python3 app.py

# Option B: Use setup script
./setup_cluster.sh ~/.kube/config
```

### Step 4: Access Web UI

Open in browser:
```
http://127.0.0.1:5000
```

You should now see:
- Real cluster nodes (not demo nodes)
- Actual pod counts
- Live metrics from your cluster
- Functional buttons to taint/drain real nodes

## Files Overview

### Frontend Files
- **`index.html`** - Web UI layout and structure
- **`styles.css`** - Styling and responsive design
- **`script.js`** - Frontend logic, API calls, live updates

### Backend Files
- **`app.py`** - Main Flask application, REST API endpoints
- **`kubernetes_manager.py`** - K8s client wrapper for node operations
- **`ml_decision_engine.py`** - ML model for risk prediction
- **`event_manager.py`** - Event logging and management

### Configuration & Deployment
- **`Dockerfile`** - Container image definition
- **`docker-compose.yml`** - Local Docker Compose setup
- **`requirements.txt`** - Python dependencies
- **`k8s/backend-deployment.yaml`** - Kubernetes manifests

### Documentation
- **`CLUSTER_SETUP.md`** - Detailed cluster integration guide
- **`CLUSTER_INTEGRATION.md`** - Architecture and workflows
- **`API.md`** - Complete REST API documentation
- **`QUICKSTART.md`** - Get started quickly
- **`README.md`** - Project overview

### Scripts
- **`validate_cluster.py`** - Check cluster readiness
- **`setup_cluster.bat`** - Windows cluster setup helper
- **`setup_cluster.sh`** - Linux/Mac cluster setup helper
- **`live_action_test.py`** - Test backend endpoints
- **`taint_tests.py`** - Unit tests for taint/drain/remove
- **`verify.py`** - System verification script

## What Each Feature Does

### Demo Mode (Current)
- 5 simulated worker nodes with random metrics
- All operations are in memory (no real cluster)
- Perfect for testing UI and workflows
- No kubeconfig required

### Cluster Mode (With Real K8s)
- Connects to actual Kubernetes cluster via kubeconfig
- Shows real node metrics (CPU, memory, temperature, etc.)
- Pod counts are live from cluster
- Taint/Drain/Remove operations execute on real nodes
- Events log actual cluster changes

### Node Tainting
```
Effect: Prevents NEW pods from scheduling
Status: Orange indicator, badge shows taint
Use: Isolate degrading nodes without disrupting workloads
Revert: Click "Remove Taint"
```

### Node Draining
```
Effect: Evicts existing pods gracefully
Status: Pods moved to other nodes (grace period: 30s)
Use: Prepare node for maintenance/upgrade
Note: System pods never evicted
```

### ML Risk Detection
Predicts node degradation using:
- CPU usage
- Memory usage  
- Temperature
- Network latency
- Disk I/O

Risk score (0-1): Shows likelihood of failure

## API Examples

**Get all nodes:**
```bash
curl http://127.0.0.1:5000/api/nodes | jq
```

**Taint a node:**
```bash
curl -X POST http://127.0.0.1:5000/api/nodes/worker-01/taint \
  -H "Content-Type: application/json" \
  -d '{"taint":"degradation=true:NoSchedule"}'
```

**Drain a node:**
```bash
curl -X POST http://127.0.0.1:5000/api/nodes/worker-01/drain \
  -H "Content-Type: application/json" \
  -d '{"grace_period": 30}'
```

**Get events:**
```bash
curl http://127.0.0.1:5000/api/events | jq
```

See **API.md** for complete documentation.

## Docker Usage

**Build:**
```bash
docker build -t predictive-infra .
```

**Run with demo data:**
```bash
docker run -p 5000:5000 predictive-infra
```

**Run with real cluster (mount kubeconfig):**
```bash
docker run -p 5000:5000 \
  -v ~/.kube/config:/app/kubeconfig:ro \
  -e KUBECONFIG=/app/kubeconfig \
  predictive-infra
```

**Use Docker Compose:**
```bash
docker-compose up
```

## Kubernetes Deployment

Deploy to a Kubernetes cluster:

```bash
# Apply manifests
kubectl apply -f k8s/backend-deployment.yaml

# Check deployment
kubectl get pods -n default
kubectl get svc backend-service

# Access via port-forward
kubectl port-forward svc/backend-service 5000:5000
```

See `k8s/backend-deployment.yaml` for details.

## System Requirements

### Minimum (Demo Mode)
- Python 3.7+
- 100 MB RAM
- Flask, scikit-learn, Kubernetes client

### For Real Cluster
- All of above +
- Access to Kubernetes cluster
- Kubeconfig file with proper permissions
- Network connectivity to cluster API

### Optional
- Docker (for containerized deployment)
- kubectl (for CLI testing)

## Troubleshooting

### Backend won't start
```bash
# Check Python
python --version

# Check dependencies
pip list | grep -E "flask|kubernetes|scikit"

# Run verification
python verify.py
```

### Cluster connection fails
```bash
# Check kubeconfig exists
ls ~/.kube/config
# or: dir %USERPROFILE%\.kube\config (Windows)

# Test cluster access
kubectl get nodes

# Validate with system
python validate_cluster.py
```

### Operations silently fail
- Backend likely in demo mode
- Check app.py logs for initialization errors
- Verify kubeconfig is readable
- See CLUSTER_SETUP.md troubleshooting section

### Buttons not working
- Refresh browser (Ctrl+R or Cmd+R)
- Check browser console (F12 → Console tab)
- Verify backend health: http://127.0.0.1:5000/api/health
- Check event log for errors

## Production Considerations

Before deploying to production:

- [ ] **Authentication**: Add API key or OAuth2
- [ ] **Rate limiting**: Implement to prevent abuse
- [ ] **Backup**: Test restore procedures before drain operations
- [ ] **Monitoring**: Monitor system resource usage
- [ ] **Logging**: Enable audit logging for operations
- [ ] **Testing**: Test on non-production cluster first
- [ ] **Permissions**: Use minimal RBAC role
- [ ] **Network**: Run in private network, not exposed to internet

## Next Steps

1. **Test Demo Mode** (already running)
   - Click buttons in UI
   - View events in log
   - Check API endpoints

2. **Connect to Test Cluster** (if you have one)
   - Get kubeconfig from admin
   - Run `validate_cluster.py`
   - Use `setup_cluster.bat` or `setup_cluster.sh`
   - Test operations on non-critical nodes

3. **Deploy to Production** (when ready)
   - Use Docker Compose for local multi-container
   - Use K8s manifests for cluster deployment
   - Implement proper RBAC and authentication
   - Monitor operations and logs

4. **Customize** (as needed)
   - Adjust monitoring intervals in `app.py`
   - Modify taint keys/effects for your needs
   - Create custom drain grace periods
   - Add more ML features

## Support Resources

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Scikit-learn ML**: https://scikit-learn.org/

## Summary

You now have a production-ready system for:
- ✅ Monitoring Kubernetes nodes
- ✅ Predicting degradation with ML
- ✅ Automating node maintenance (taint/drain)
- ✅ Tracking all operations via events
- ✅ Accessing via web UI or REST API

**Ready to try it?**

1. The UI is live at: http://127.0.0.1:5000
2. Try clicking "Taint", "Drain", "Remove Taint" buttons
3. Watch the event log for live updates
4. Check the API: http://127.0.0.1:5000/api/health

Enjoy! 🚀
