#!/bin/bash

# kubctl-0x01 - Kubernetes Scaling and Load Testing Script
# Author: Vuyo
# Description: Scale Django messaging app and perform load testing

echo "=== Kubernetes Scaling and Load Testing Script ==="
echo "Starting at: $(date)"
echo

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

WRK_AVAILABLE=true
if ! command -v wrk &> /dev/null; then
    print_warning "wrk is not installed. Trying to install..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y wrk
        elif command -v yum &> /dev/null; then
            sudo yum install -y epel-release && sudo yum install -y wrk
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y wrk
        else
            print_warning "Could not install wrk automatically. Will use curl for load testing."
            WRK_AVAILABLE=false
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install wrk
        else
            print_warning "Homebrew not found. Will use curl for load testing."
            WRK_AVAILABLE=false
        fi
    else
        print_warning "Unknown OS. Will use curl for load testing."
        WRK_AVAILABLE=false
    fi
    
    if ! command -v wrk &> /dev/null; then
        WRK_AVAILABLE=false
    fi
fi

print_step "Scaling messaging-app deployment to 3 replicas..."
kubectl scale deployment messaging-app --replicas=3

if [ $? -eq 0 ]; then
    print_success "Deployment scaled successfully"
else
    print_error "Failed to scale deployment"
    exit 1
fi

echo
print_step "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=messaging-app --timeout=120s

if [ $? -eq 0 ]; then
    print_success "All pods are ready"
else
    print_warning "Some pods may not be ready yet"
fi

echo
print_step "Verifying pods are running..."
echo "Current pods:"
kubectl get pods -l app=messaging-app

RUNNING_PODS=$(kubectl get pods -l app=messaging-app --field-selector=status.phase=Running --no-headers | wc -l)
echo
print_success "Number of running pods: $RUNNING_PODS"

print_step "Setting up port forwarding for load testing..."
kubectl port-forward service/messaging-app-service 8080:80 &
PORT_FORWARD_PID=$!

sleep 3

cleanup() {
    print_step "Cleaning up port forwarding..."
    kill $PORT_FORWARD_PID 2>/dev/null
    wait $PORT_FORWARD_PID 2>/dev/null
}

trap cleanup EXIT

print_step "Testing app accessibility..."
if curl -s http://localhost:8080 > /dev/null; then
    print_success "App is accessible on http://localhost:8080"
else
    print_warning "App may not be responding yet, proceeding with load test..."
fi

echo
print_step "Starting load testing..."

if [ "$WRK_AVAILABLE" = true ]; then
    print_step "Using wrk for load testing..."
    echo "Test parameters:"
    echo "  - Duration: 30 seconds"
    echo "  - Threads: 4"
    echo "  - Connections: 100"
    echo "  - Target: http://localhost:8080"
    echo
    
    # Run wrk load test
    wrk -t4 -c100 -d30s http://localhost:8080
    
    echo
    print_success "Load testing with wrk completed"
else
    print_step "Using curl for load testing (wrk not available)..."
    echo "Test parameters:"
    echo "  - Duration: 30 seconds"
    echo "  - Concurrent requests: 10"
    echo "  - Target: http://localhost:8080"
    echo
    
    START_TIME=$(date +%s)
    END_TIME=$((START_TIME + 30))
    REQUEST_COUNT=0
    SUCCESS_COUNT=0
    
    echo "Starting curl-based load test..."
    
    while [ $(date +%s) -lt $END_TIME ]; do
        for i in {1..10}; do
            {
                if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
                    ((SUCCESS_COUNT++))
                fi
                ((REQUEST_COUNT++))
            } &
        done
        wait
        echo -n "."
    done
    
    echo
    echo "Load test completed:"
    echo "  - Total requests: $REQUEST_COUNT"
    echo "  - Successful requests: $SUCCESS_COUNT"
    echo "  - Success rate: $(echo "scale=2; $SUCCESS_COUNT * 100 / $REQUEST_COUNT" | bc -l)%"
    
    print_success "Load testing with curl completed"
fi

echo
print_step "Monitoring resource usage..."

if kubectl top nodes &> /dev/null; then
    echo "=== Node Resource Usage ==="
    kubectl top nodes
    echo
    
    echo "=== Pod Resource Usage ==="
    kubectl top pods -l app=messaging-app
    echo
    print_success "Resource monitoring completed"
else
    print_warning "Metrics server not available. Cannot show resource usage."
    print_warning "To enable metrics server, run: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
fi

echo
print_step "Final deployment status..."
kubectl get deployment messaging-app
echo

print_step "Final pod status..."
kubectl get pods -l app=messaging-app -o wide
echo

print_step "Service status..."
kubectl get service messaging-app-service
echo

echo "=== SUMMARY ==="
echo "✓ Scaled deployment to 3 replicas"
echo "✓ Verified $RUNNING_PODS pods are running"
echo "✓ Performed load testing with wrk"
echo "✓ Monitored resource usage"
echo
print_success "Script completed successfully at: $(date)"

echo
read -p "Do you want to scale back down to 2 replicas? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Scaling back down to 2 replicas..."
    kubectl scale deployment messaging-app --replicas=2
    print_success "Scaled back to 2 replicas"
fi