#!/bin/bash

# kubectl-0x02.sh - Blue-Green Deployment Script
# This script performs zero-downtime deployments using blue-green strategy

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to wait for deployment to be ready
wait_for_deployment() {
    local deployment_name=$1
    local timeout=300  # 5 minutes timeout
    
    print_status "Waiting for deployment $deployment_name to be ready..."
    
    if kubectl wait --for=condition=available --timeout=${timeout}s deployment/$deployment_name; then
        print_success "Deployment $deployment_name is ready!"
        return 0
    else
        print_error "Deployment $deployment_name failed to become ready within $timeout seconds"
        return 1
    fi
}

# Function to check pod health
check_pod_health() {
    local version=$1
    local service_name="messaging-app-${version}-service"
    
    print_status "Checking health of $version deployment..."
    
    # Get pod names for the version
    local pods=$(kubectl get pods -l app=messaging-app,version=$version -o jsonpath='{.items[*].metadata.name}')
    
    if [ -z "$pods" ]; then
        print_error "No pods found for $version deployment"
        return 1
    fi
    
    # Check logs for errors
    for pod in $pods; do
        print_status "Checking logs for pod: $pod"
        
        # Get recent logs and check for common error patterns
        local logs=$(kubectl logs $pod --tail=50 || true)
        
        if echo "$logs" | grep -i "error\|exception\|traceback\|fatal" > /dev/null; then
            print_warning "Potential errors found in $pod logs:"
            echo "$logs" | grep -i "error\|exception\|traceback\|fatal" | head -5
        else
            print_success "No obvious errors in $pod logs"
        fi
    done
    
    # Test service connectivity
    print_status "Testing $service_name connectivity..."
    if kubectl run test-pod-$version --rm -i --restart=Never --image=curlimages/curl:latest -- curl -s -o /dev/null -w "%{http_code}" http://$service_name:8000 | grep -q "200"; then
        print_success "$service_name is responding correctly"
        return 0
    else
        print_error "$service_name is not responding correctly"
        return 1
    fi
}

# Function to switch traffic
switch_traffic() {
    local target_version=$1
    
    print_status "Switching traffic to $target_version deployment..."
    
    # Update the main service to point to the target version
    kubectl patch service messaging-app-service -p '{"spec":{"selector":{"app":"messaging-app","version":"'$target_version'"}}}'
    
    # Wait a moment for the change to propagate
    sleep 5
    
    # Test the main service
    print_status "Testing main service after traffic switch..."
    if kubectl run test-main-service --rm -i --restart=Never --image=curlimages/curl:latest -- curl -s -o /dev/null -w "%{http_code}" http://messaging-app-service:8000 | grep -q "200"; then
        print_success "Traffic successfully switched to $target_version"
        return 0
    else
        print_error "Traffic switch failed - main service not responding"
        return 1
    fi
}

# Function to rollback
rollback() {
    local rollback_version=$1
    print_warning "Rolling back to $rollback_version deployment..."
    switch_traffic $rollback_version
}

# Function to cleanup old deployment
cleanup_old_deployment() {
    local old_version=$1
    
    read -p "Do you want to delete the old $old_version deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deleting $old_version deployment..."
        kubectl delete deployment messaging-app-$old_version
        kubectl delete service messaging-app-${old_version}-service
        print_success "Old $old_version deployment cleaned up"
    else
        print_status "Keeping $old_version deployment for rollback purposes"
    fi
}

# Main deployment function
main() {
    print_status "Starting Blue-Green Deployment Process..."
    
    # Check if this is initial deployment or update
    if kubectl get deployment messaging-app-blue > /dev/null 2>&1; then
        print_status "Blue deployment exists. Deploying green version..."
        TARGET_VERSION="green"
        OLD_VERSION="blue"
    elif kubectl get deployment messaging-app-green > /dev/null 2>&1; then
        print_status "Green deployment exists. Deploying blue version..."
        TARGET_VERSION="blue"
        OLD_VERSION="green"
    else
        print_status "No existing deployment found. Starting with blue version..."
        TARGET_VERSION="blue"
        OLD_VERSION=""
    fi
    
    print_status "Deploying $TARGET_VERSION version..."
    
    # Deploy the new version
    if [ "$TARGET_VERSION" == "blue" ]; then
        kubectl apply -f blue_deployment.yaml
    else
        kubectl apply -f green_deployment.yaml
    fi
    
    # Deploy services
    kubectl apply -f kubeservice.yaml
    
    # Wait for deployment to be ready
    if ! wait_for_deployment "messaging-app-$TARGET_VERSION"; then
        print_error "New deployment failed to become ready"
        exit 1
    fi
    
    # Check health of new deployment
    if ! check_pod_health "$TARGET_VERSION"; then
        print_error "Health check failed for new deployment"
        if [ -n "$OLD_VERSION" ]; then
            rollback "$OLD_VERSION"
        fi
        exit 1
    fi
    
    # Switch traffic to new version
    if ! switch_traffic "$TARGET_VERSION"; then
        print_error "Traffic switch failed"
        if [ -n "$OLD_VERSION" ]; then
            rollback "$OLD_VERSION"
        fi
        exit 1
    fi
    
    print_success "Deployment completed successfully!"
    
    # Show current status
    print_status "Current deployment status:"
    kubectl get deployments -l app=messaging-app
    kubectl get services -l app=messaging-app
    
    # Option to cleanup old deployment
    if [ -n "$OLD_VERSION" ]; then
        cleanup_old_deployment "$OLD_VERSION"
    fi
    
    print_success "Blue-Green deployment process completed!"
}

# Script usage
case "${1:-}" in
    "rollback")
        if [ -z "$2" ]; then
            print_error "Usage: $0 rollback <blue|green>"
            exit 1
        fi
        rollback "$2"
        ;;
    "status")
        print_status "Current deployment status:"
        kubectl get deployments -l app=messaging-app
        kubectl get services -l app=messaging-app
        kubectl get pods -l app=messaging-app
        ;;
    "logs")
        VERSION=${2:-"all"}
        if [ "$VERSION" == "all" ]; then
            print_status "Logs for all deployments:"
            kubectl logs -l app=messaging-app --tail=20
        else
            print_status "Logs for $VERSION deployment:"
            kubectl logs -l app=messaging-app,version=$VERSION --tail=20
        fi
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [rollback <blue|green>|status|logs [blue|green|all]]"
        echo "  No arguments: Perform blue-green deployment"
        echo "  rollback <version>: Rollback to specified version"
        echo "  status: Show current deployment status"
        echo "  logs [version]: Show logs for specified version or all"
        exit 1
        ;;
esac