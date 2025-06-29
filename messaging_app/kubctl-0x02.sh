#!/bin/bash

# Blue-Green Deployment Script

echo "Deploying Blue (v1) and Green (v2) versions..."
kubectl apply -f blue_deployment.yaml
kubectl apply -f green_deployment.yaml

echo -e "\nChecking Green version logs:"
GREEN_POD=$(kubectl get pods -l version=2.0 -o jsonpath='{.items[0].metadata.name}')
kubectl logs $GREEN_POD --tail=50

read -p "Does the Green version look healthy? Switch traffic? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Switching traffic to Green version..."
  kubectl patch service django-router -p '{"spec":{"selector":{"version":"2.0"}}}'
  echo "Traffic switched to Green version"
  echo "Scaling down Blue version..."
  kubectl scale deployment django-app-blue --replicas=0
  echo "Blue version scaled down"
else
  echo "Keeping traffic on Blue version"
  kubectl delete deployment django-app-green
  echo "Green version removed"
fi

echo -e "\nCurrent deployments:"
kubectl get deployments -l app=django

echo -e "\nService routing:"
kubectl describe service django-router | grep -A2 Selector