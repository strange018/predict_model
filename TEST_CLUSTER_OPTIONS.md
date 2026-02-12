# Connect to a Test Kubernetes Cluster

You don't currently have a kubeconfig file. Here are your options to get one:

## Option 1: Use a Cloud Provider (Easiest)

### AWS EKS
**Prerequisites:** AWS account, `aws` CLI installed on your machine

```powershell
# Install AWS CLI (Windows): https://aws.amazon.com/cli/

# Login to AWS
aws configure

# List your EKS clusters
aws eks list-clusters --region us-east-1

# Get credentials for your cluster
aws eks update-kubeconfig --name YOUR_CLUSTER_NAME --region YOUR_REGION

# Verify
kubectl get nodes
```

**Then start the system:**
```powershell
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config"
python app.py
```

### Google GKE
**Prerequisites:** Google Cloud account, `gcloud` CLI installed

```powershell
# Install gcloud: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# List clusters
gcloud container clusters list

# Get credentials
gcloud container clusters get-credentials YOUR_CLUSTER_NAME --zone YOUR_ZONE

# Verify
kubectl get nodes
```

**Then start the system:**
```powershell
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config"
python app.py
```

### Azure AKS
**Prerequisites:** Azure account, `az` CLI installed

```powershell
# Install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# Login
az login

# Set subscription
az account set --subscription YOUR_SUBSCRIPTION_ID

# List clusters
az aks list --output table

# Get credentials
az aks get-credentials --resource-group YOUR_RG --name YOUR_CLUSTER_NAME

# Verify
kubectl get nodes
```

**Then start the system:**
```powershell
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config"
python app.py
```

---

## Option 2: Local Test Cluster (Free, No Cloud Account Needed)

### Install Minikube
Minikube runs a single-node K8s cluster locally in a VM.

**Step 1: Install Minikube**
```powershell
# Download installer: https://minikube.sigs.k8s.io/docs/start/
# Or using Chocolatey:
choco install minikube

# Verify
minikube version
```

**Step 2: Start Minikube**
```powershell
# Start cluster (first time takes 2-3 minutes)
minikube start --driver hyperv

# Or with VirtualBox:
minikube start --driver virtualbox

# Check status
minikube status
```

**Step 3: Use kubectl**
```powershell
# Minikube automatically updates kubeconfig
kubectl get nodes

# You should see one node: "minikube"
```

**Step 4: Start the Predictive Infrastructure System**
```powershell
# Kubeconfig is already set up by minikube
python validate_cluster.py

# If validation passes:
python app.py
```

**Step 5: Open UI**
```
http://127.0.0.1:5000
```

You should see: **1 minikube node** with test operations enabled.

### Alternative: Kind (Kubernetes in Docker)
If you prefer Docker over a full VM:

```powershell
# Install Kind: https://kind.sigs.k8s.io/docs/user/quick-start/
# Download binary from: https://github.com/kubernetes-sigs/kind/releases

# Create cluster
kind create cluster --name test-cluster

# Verify
kubectl get nodes
# You should see: "test-cluster-control-plane"

# Start the system
python app.py
```

---

## Quickest Path (Demo Mode)

If you just want to **test UI/buttons without a cluster**:

```powershell
# Already running with demo nodes
http://127.0.0.1:5000

# Click buttons, they work in demo mode
# No kubeconfig needed
```

---

## Workflow Summary

```
┌─────────────────────────────────────────┐
│  Do you have Kubernetes cluster?        │
└─────────────────────────────────────────┘
         ↙                           ↘
    YES                             NO
     ↓                               ↓
┌──────────┐                  ┌──────────────────┐
│ Get      │                  │ Choose option:   │
│ kubeconfig                  │ • Cloud (AWS/GKE)│
└──────────┘                  │ • Local Minikube │
     ↓                         │ • Demo Mode      │
┌──────────┐                  └──────────────────┘
│ Run      │                        ↓
│validate_ │                  ┌──────────────────┐
│cluster.py│                  │ Follow setup     │
└──────────┘                  │ instructions →   │
     ↓                        └──────────────────┘
┌──────────┐                        ↓
│ python   │                  ┌──────────────────┐
│ app.py   │                  │ python app.py    │
└──────────┘                  │ (or minikube)    │
     ↓                        └──────────────────┘
┌──────────┐                        ↓
│ Connect  │                  ┌──────────────────┐
│ to       │                  │ http://127.0.0.1 │
│ cluster  │                  │ :5000            │
└──────────┘                  └──────────────────┘
```

---

## Recommended Option

### For Production/Real Testing:
**AWS EKS** - Most common, good free tier trial included

### For Local Development/Testing:
**Minikube** - No cloud account needed, fast, isolated

### For Quick Testing:
**Demo mode** - Already running, click buttons in UI

---

## Next Steps

1. **Choose your option** (cloud, minikube, or demo)
2. **If cloud:** Follow the provider-specific steps above
3. **If minikube:** Run the Minikube steps
4. **If demo:** Already working! Just refresh http://127.0.0.1:5000

Once you have kubeconfig:
```powershell
# Validate
python validate_cluster.py

# If all ✓, connect system to cluster
python app.py

# Open UI
http://127.0.0.1:5000
```

---

## Troubleshooting

### Can't find CLI tools
- AWS CLI: https://aws.amazon.com/cli/
- gcloud: https://cloud.google.com/sdk/
- Azure CLI: https://learn.microsoft.com/en-us/cli/azure/
- kubectl: https://kubernetes.io/docs/tasks/tools/
- Minikube: https://minikube.sigs.k8s.io/

### kubectl command not found
```powershell
# Install kubectl separately
# Or use cloud provider CLI which includes kubectl
```

### Cluster connection failing
```powershell
# Verify credentials are set up
kubectl get nodes

# Check current context
kubectl config current-context

# List available contexts
kubectl config get-contexts
```

---

**Ready? Choose your option and let me help you set it up!** 🚀

Current status:
- ✅ Demo mode running on http://127.0.0.1:5000
- ❌ No real cluster connected yet
- ⏳ Waiting for kubeconfig...
