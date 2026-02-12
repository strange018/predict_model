#!/bin/bash
# Cluster Integration Setup Script for Linux/Mac
# This script helps set up KUBECONFIG and validate cluster connection

set -e

echo ""
echo "========================================="
echo "Predictive Infrastructure - Cluster Setup"
echo "========================================="
echo ""

# Check if kubeconfig path provided
if [ -z "$1" ]; then
    echo "Usage: ./setup_cluster.sh /path/to/kubeconfig"
    echo ""
    echo "Example:"
    echo "  ./setup_cluster.sh ~/.kube/config"
    echo ""
    echo "Or set KUBECONFIG manually:"
    echo "  export KUBECONFIG=/path/to/kubeconfig"
    echo "  python3 app.py"
    echo ""
    exit 1
fi

KUBECONFIG="$1"

if [ ! -f "$KUBECONFIG" ]; then
    echo "Error: Kubeconfig file not found: $KUBECONFIG"
    exit 1
fi

echo "Found kubeconfig: $KUBECONFIG"
echo ""

# Set environment variable for this session
export KUBECONFIG="$KUBECONFIG"

echo "Setting KUBECONFIG for this session..."
echo "KUBECONFIG=$KUBECONFIG"
echo ""

# Run validation
echo "Running validation..."
python3 validate_cluster.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Validation failed. Please check the errors above."
    exit 1
fi

echo ""
echo "========================================="
echo "Setup Complete! Starting application..."
echo "========================================="
echo ""

# Start the application
python3 app.py
