# Kubernetes Cluster Integration Guide

## Overview
This system can connect to a real Kubernetes cluster to perform live node operations (taint, drain, remove-taint).

## Prerequisites

1. **Kubernetes Cluster Access**
   - A running Kubernetes cluster (v1.20+)
   - `kubectl` installed locally
   - Valid kubeconfig file with cluster credentials

2. **Python Environment**
   - Python 3.7+
   - All dependencies installed (see `requirements.txt`)

## Setup Steps

### Step 1: Get Your Kubeconfig

```bash
# If using cloud provider (AWS EKS):
aws eks update-kubeconfig --name YOUR_CLUSTER_NAME --region YOUR_REGION

# If using cloud provider (GKE):
gcloud container clusters get-credentials YOUR_CLUSTER_NAME --zone YOUR_ZONE

# If using cloud provider (AKS):
az aks get-credentials --resource-group YOUR_RG --name YOUR_CLUSTER_NAME

# If you have kubeconfig file already:
# Copy it to a known location (default: ~/.kube/config)
```

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:KUBECONFIG = "C:\path\to\your\kubeconfig"
# Then run:
python app.py
```

**Windows (Command Prompt):**
```cmd
set KUBECONFIG=C:\path\to\your\kubeconfig
python app.py
```

**Linux/Mac:**
```bash
export KUBECONFIG=/path/to/your/kubeconfig
python app.py
```

Or use the default location:
```bash
# Default: ~/.kube/config
# The system will automatically use this if KUBECONFIG is not set
```

### Step 3: Validate Cluster Connection

```bash
python validate_cluster.py
```

This will:
- Check kubeconfig file exists and is readable
- Verify Kubernetes API connectivity
- List available nodes
- Test taint/drain permissions
- Show system readiness

### Step 4: Run the System

```bash
# Start the backend (connects to real cluster)
python app.py

# In another terminal, for development:
# Or use Docker Compose to run in container
```

## Testing

### Using the UI
1. Open browser to `http://127.0.0.1:5000`
2. View live nodes from your cluster
3. Click Taint/Drain/Remove Taint buttons to execute operations
4. Check events log for operation results

### Using CLI
```bash
# Apply taint to a node
curl -X POST http://127.0.0.1:5000/api/nodes/YOUR_NODE_ID/taint \
  -H "Content-Type: application/json" \
  -d '{"taint": "degradation=true:NoSchedule"}'

# Drain a node
curl -X POST http://127.0.0.1:5000/api/nodes/YOUR_NODE_ID/drain \
  -H "Content-Type: application/json" \
  -d '{"grace_period": 30}'

# Remove taint
curl -X POST http://127.0.0.1:5000/api/nodes/YOUR_NODE_ID/remove-taint \
  -H "Content-Type: application/json" \
  -d '{"key": "degradation"}'
```

## Troubleshooting

### "Could not load Kubernetes config"
- **Cause**: Kubeconfig file not found or invalid
- **Fix**: 
  1. Verify file exists: `ls $KUBECONFIG` or `dir %KUBECONFIG%`
  2. Verify format: `kubectl config view --kubeconfig=YOUR_FILE`
  3. Set KUBECONFIG env var and restart app

### "Unauthorized" errors
- **Cause**: Missing or invalid credentials in kubeconfig
- **Fix**:
  1. Verify cluster authentication: `kubectl auth can-i get nodes`
  2. Get fresh credentials: `aws eks update-kubeconfig` (or cloud equivalent)
  3. Verify RBAC permissions (see RBAC section below)

### Nodes can't be found
- **Cause**: Cluster context is wrong
- **Fix**: 
  1. List available contexts: `kubectl config get-contexts`
  2. Switch context: `kubectl config use-context YOUR_CONTEXT`

### Operations succeed but don't affect cluster
- **Cause**: Running in demo mode (kubeconfig failed silently)
- **Fix**: Check application logs for K8s initialization warnings

## RBAC Requirements

The user running this system needs the following Kubernetes permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: predictive-infra-role
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "patch"]
- apiGroups: [""]
  resources: ["pods"]
  resources: ["pods/eviction"]
  verbs: ["create", "list", "get"]
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "list"]
```

Request these permissions from your cluster administrator if needed.

## Environment Variables

### KUBECONFIG
Location of your kubeconfig file. If not set, defaults to `~/.kube/config`.

```
KUBECONFIG=/path/to/kubeconfig
```

### Other Options
- `LOG_LEVEL`: Set to `DEBUG` for verbose logging
- `API_PORT`: Change port (default 5000)

## Docker Setup

To run in a container against a real cluster:

```bash
# Build image
docker build -t predictive-infra .

# Run with kubeconfig mounted
docker run -it \
  -v $HOME/.kube/config:/app/kubeconfig:ro \
  -e KUBECONFIG=/app/kubeconfig \
  -p 5000:5000 \
  predictive-infra
```

## Production Considerations

1. **ServiceAccount**: For in-cluster deployments, use a ServiceAccount with appropriate RBAC
2. **Monitoring**: Monitor node operations; drain operations can impact workloads
3. **Backups**: Ensure workloads have backups before drain operations
4. **Testing**: Test on non-production cluster first
5. **Audit**: Enable Kubernetes audit logging to track operations

## Support

For issues:
1. Check logs: `docker logs <container>` or terminal output
2. Verify cluster connectivity: `kubectl get nodes`
3. Test permissions: `kubectl auth can-i patch nodes`
4. Review events: `kubectl get events -A`
