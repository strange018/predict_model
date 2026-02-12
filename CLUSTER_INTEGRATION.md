# Cluster Integration: Real Kubernetes Support

This guide explains how to connect the Predictive Infrastructure system to a **real Kubernetes cluster** for live node operations.

## Quick Start

### Option 1: Set KUBECONFIG and Run (Windows)

```powershell
$env:KUBECONFIG = "C:\path\to\your\kubeconfig"
python app.py
```

Or use the setup script:
```powershell
.\setup_cluster.bat "C:\path\to\your\kubeconfig"
```

### Option 2: Set KUBECONFIG and Run (Linux/Mac)

```bash
export KUBECONFIG=/path/to/your/kubeconfig
python3 app.py
```

Or use the setup script:
```bash
./setup_cluster.sh /path/to/your/kubeconfig
```

### Option 3: Use Default Location

If your kubeconfig is at `~/.kube/config`, just run:
```bash
python app.py
```

## Getting Your Kubeconfig

### AWS EKS
```bash
aws eks update-kubeconfig --name YOUR_CLUSTER_NAME --region YOUR_REGION
```

### Google GKE
```bash
gcloud container clusters get-credentials YOUR_CLUSTER_NAME --zone YOUR_ZONE
```

### Azure AKS
```bash
az aks get-credentials --resource-group YOUR_RG --name YOUR_CLUSTER_NAME
```

### Other Clusters
Contact your cluster administrator for the kubeconfig file.

## Validation

Before running against a real cluster, validate your setup:

```bash
python validate_cluster.py
```

This checks:
- ✓ Kubeconfig file exists and is readable
- ✓ Kubernetes client library is installed
- ✓ Connection to cluster API
- ✓ RBAC permissions for node operations
- ✓ Lists available nodes

## System Architecture

When connected to a real cluster:

```
┌─────────────────────────────────────────┐
│        Frontend Browser                 │
│   (http://127.0.0.1:5000)              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Flask Backend (app.py)                │
│  ┌────────────────────────────────────┐ │
│  │  KubernetesManager                 │ │
│  │  - Node metrics from cluster       │ │
│  │  - Apply/remove taints             │ │
│  │  - Drain nodes                     │ │
│  │  - Evict pods from nodes           │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
               ▼ (via kubeconfig)
┌─────────────────────────────────────────┐
│   Real Kubernetes Cluster               │
│  - Worker nodes                         │
│  - Running pods/workloads               │
│  - Kubernetes API                       │
└─────────────────────────────────────────┘
```

## How It Works

### 1. Node Discovery
- **Demo Mode**: Simulates 5 worker nodes with random metrics
- **Cluster Mode**: Connects to real cluster, fetches actual node metrics

### 2. Monitoring
Backend continuously polls cluster for:
- Node resource usage (CPU, memory)
- Pod placement
- Current taints
- Node conditions

### 3. Actions
When you click buttons in the UI:

#### Taint Node
- Prevents new pods from scheduling on degraded nodes
- Existing pods continue running
- Backend stores taint state

#### Drain Node
- Gracefully evicts all user pods from node
- System pods (kube-system) are skipped
- Pods are evicted with 30-second grace period

#### Remove Taint
- Restores node to acceptable state
- New pods can schedule again
- System continues monitoring

## Event Flow

```
1. User clicks "Taint" button on node-01
   ↓
2. Frontend sends POST /api/nodes/node-01/taint
   ↓
3. Backend receives request
   ├─ If cluster connected: Call Kubernetes API
   │  └─ Patch node spec.taints
   └─ If demo mode: Update in-memory node state
   ↓
4. Backend logs event: "Node Tainted"
   ├─ Emit via /api/events endpoint
   └─ Subscribe via /api/events/stream (SSE)
   ↓
5. Frontend receives event
   ├─ Auto-refresh node metrics
   ├─ Show taint badge on node card
   ├─ Update status indicator color
   └─ Disable "Taint" button, enable "Remove Taint"
```

## Real Cluster Testing Checklist

- [ ] Kubeconfig set and validated
- [ ] `python validate_cluster.py` passes
- [ ] Backend starts without K8s errors
- [ ] Frontend loads (http://127.0.0.1:5000)
- [ ] Nodes appear in UI (not demo nodes)
- [ ] Can click "Taint" button
- [ ] Taint applied visible in cluster: `kubectl get nodes -o jsonpath=...`
- [ ] Event log shows action
- [ ] Can click "Drain" button
- [ ] Pods evicted from node visible via `kubectl get pods -o wide`
- [ ] Can click "Remove Taint"
- [ ] Taint removed, node recovers

## Permissions Required

The kubeconfig user needs these Kubernetes permissions:

```yaml
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "patch"]
  
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
  
- apiGroups: [""]
  resources: ["pods/eviction"]
  verbs: ["create"]
  
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "list"]
```

Ask your cluster admin to grant these if you see "Forbidden" errors.

## Troubleshooting

### Cluster not showing nodes
```bash
# Check kubeconfig
kubectl config current-context
kubectl get nodes

# Check logs
python app.py  # Look for K8s manager errors
```

### Operations fail silently
The system might be running in demo mode. Check backend logs for:
```
ERROR:__main__:✗ Failed to initialize: ...
```
If present, kubeconfig failed to load.

### Permission denied on taint/drain
```bash
# Check your permissions
kubectl auth can-i patch nodes
kubectl auth can-i create pods/eviction

# Ask cluster admin for RBAC role
```

### Node drains take too long
The system uses 30-second grace period. Some stateful workloads may need migration time. You can modify `app.py` line for `drain_node()`.

## Performance Notes

### Cluster Mode
- Initial load: 1-2 seconds (API calls)
- Polling interval: 3 seconds per node batch
- Taint/Drain operations: 5-60 seconds (depends on pod count)

### Demo Mode
- Instant (in-memory operations)
- Good for testing UI/workflows without cluster

## Deployment Options

### Local Development
```bash
export KUBECONFIG=~/.kube/config
python app.py
```

### Docker Container (Local)
```bash
docker build -t predictive-infra .
docker run -it \
  -v ~/.kube/config:/app/kubeconfig:ro \
  -e KUBECONFIG=/app/kubeconfig \
  -p 5000:5000 \
  predictive-infra
```

### Kubernetes Deployment
See `k8s/backend-deployment.yaml`:
- ServiceAccount with RBAC role
- Pod mounted with cluster credentials
- Exposes via Service

## Next Steps

1. **Get kubeconfig** from your cluster admin or cloud provider
2. **Run validation**: `python validate_cluster.py`
3. **Start backend**: `python app.py`
4. **Open UI**: http://127.0.0.1:5000
5. **Test operations** on a non-prod cluster first
6. **Monitor events** in the log for any issues

## Support

For detailed setup instructions, see [CLUSTER_SETUP.md](CLUSTER_SETUP.md).

For API documentation, see [API.md](API.md) (if available).

For Kubernetes concepts:
- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Node Capacity Management](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/)
- [Pod Disruption Budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
