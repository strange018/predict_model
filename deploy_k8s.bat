@echo off
echo Building Docker image for Kubernetes deployment (tag: infra-backend:latest)
docker build -t infra-backend:latest .
echo Applying Kubernetes manifests in ./k8s
kubectl apply -f k8s/backend-deployment.yaml
echo Deployment applied. Run 'kubectl get pods' to check status.
