# Optimized kurbeScript.ps1 for Docker/WSL2
$ErrorActionPreference = "Stop"

try {
    Write-Host "1. Verifying WSL and Docker status..."
    wsl --list --verbose
    docker version
    
    Write-Host "`n2. Cleaning any existing Minikube clusters..."
    minikube delete
    
    Write-Host "`n3. Starting Minikube with Docker driver and WSL2 integration..."
    minikube start --driver=docker --container-runtime=containerd --memory=4096 --cpus=2
    
    Write-Host "`n4. Configuring Kubernetes cluster..."
    minikube addons enable metrics-server
    kubectl config use-context minikube
    
    Write-Host "`n5. Verifying cluster status:"
    minikube status
    kubectl get nodes
    
    Write-Host "`nSetup successful! Cluster IP: $(minikube ip)"
    Write-Host "To access dashboard: minikube dashboard"
}
catch {
    Write-Host "`nError occurred: $_`n"
    Write-Host "Troubleshooting steps:"
    Write-Host "1. Ensure Docker Desktop is running with WSL2 backend"
    Write-Host "2. Check virtualization is enabled in BIOS"
    Write-Host "3. Try: wsl --update && wsl --shutdown"
    exit 1
}