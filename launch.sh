#!/bin/bash

# Predictive Infrastructure Intelligence System - Complete Launch Script (Linux/Mac)
# Usage: ./launch.sh [mode]
# Modes: demo, docker, kubernetes

set -e

MODE="${1:-demo}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check requirements
check_requirements() {
    print_header "Checking Requirements"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
    print_success "Python $(python3 --version | cut -d' ' -f2) found"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found"
        exit 1
    fi
    print_success "pip3 found"
    
    if [ "$MODE" = "docker" ]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker not found. Please install Docker"
            exit 1
        fi
        print_success "Docker found"
        
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose not found"
            exit 1
        fi
        print_success "Docker Compose found"
    fi
    
    if [ "$MODE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_error "kubectl not found. Please install kubectl"
            exit 1
        fi
        print_success "kubectl found"
    fi
}

# Setup Python environment
setup_python_env() {
    print_header "Setting Up Python Environment"
    
    cd "$PROJECT_DIR"
    
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi
    
    source venv/bin/activate
    
    print_info "Installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Dependencies installed"
}

# Demo mode - local Flask server
run_demo_mode() {
    print_header "Starting in DEMO MODE"
    
    setup_python_env
    source venv/bin/activate
    
    print_info "Starting Flask backend on http://localhost:5000..."
    echo ""
    
    cd "$PROJECT_DIR"
    FLASK_APP=app.py FLASK_ENV=development python app.py
}

# Docker mode
run_docker_mode() {
    print_header "Starting with Docker Compose"
    
    cd "$PROJECT_DIR"
    
    print_info "Building containers..."
    docker-compose build
    
    print_info "Starting services..."
    docker-compose up
    
    print_success "System running on http://localhost"
    echo ""
    print_info "To stop: docker-compose down"
}

# Kubernetes mode
run_kubernetes_mode() {
    print_header "Deploying to Kubernetes"
    
    cd "$PROJECT_DIR"
    
    print_warning "This requires an active Kubernetes cluster"
    
    # Check cluster access
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Unable to connect to Kubernetes cluster"
        print_info "Make sure you have kubectl configured and a cluster running"
        exit 1
    fi
    
    CLUSTER_NAME=$(kubectl config current-context)
    print_success "Connected to cluster: $CLUSTER_NAME"
    
    # Build and push image (requires registry)
    read -p "Enter Docker registry (or skip with 'demo'): " REGISTRY
    
    if [ "$REGISTRY" != "demo" ] && [ -n "$REGISTRY" ]; then
        print_info "Building image..."
        docker build -t "$REGISTRY/predictive-infrastructure:latest" .
        
        print_info "Pushing to registry..."
        docker push "$REGISTRY/predictive-infrastructure:latest"
        
        print_info "Updating manifests with image: $REGISTRY/predictive-infrastructure:latest"
        sed -i "s|image:.*predictive.*|image: $REGISTRY/predictive-infrastructure:latest|g" kubernetes-manifest.yaml
    fi
    
    print_info "Deploying to Kubernetes..."
    kubectl apply -f kubernetes-manifest.yaml
    
    print_success "Deployment started"
    echo ""
    print_info "Check status with:"
    echo "  kubectl get pods -n predictive-infra"
    echo "  kubectl logs -n predictive-infra -l app=predictive-backend"
}

# Main execution
main() {
    echo ""
    print_header "Predictive Infrastructure Intelligence System"
    print_info "Mode: $MODE"
    echo ""
    
    case "$MODE" in
        demo)
            check_requirements
            run_demo_mode
            ;;
        docker)
            check_requirements
            run_docker_mode
            ;;
        kubernetes)
            check_requirements
            run_kubernetes_mode
            ;;
        *)
            print_error "Invalid mode: $MODE"
            echo ""
            echo "Usage: $0 [mode]"
            echo ""
            echo "Modes:"
            echo "  demo        - Run locally in Flask (default)"
            echo "  docker      - Run with Docker Compose"
            echo "  kubernetes  - Deploy to Kubernetes cluster"
            exit 1
            ;;
    esac
}

main
