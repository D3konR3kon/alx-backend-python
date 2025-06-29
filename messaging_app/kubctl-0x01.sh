#!/bin/bash

# kubctl-0x01 - Kubernetes Scaling Demo Script

echo "Scaling Django deployment to 3 replicas..."
kubectl scale deployment django-messaging-app --replicas=3


echo -n "Waiting for pods to become ready..."
while [[ $(kubectl get pods -l app=django-messaging -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}' | tr ' ' '\n' | sort | uniq) != "True" ]]; 
do
  echo -n "."
  sleep 2
done
echo -e "\nScaled deployment ready!"

echo -e "\nCurrent pod status:"
kubectl get pods -l app=django-messaging -o wide


SERVICE_URL=$(minikube service django-messaging-service --url)
echo -e "\nService endpoint: $SERVICE_URL"


echo -e "\nStarting load test (30 seconds, 10 threads, 20 connections)..."
wrk -t10 -c20 -d30s $SERVICE_URL

echo -e "\nCurrent resource usage:"
echo "POD CPU/MEMORY:"
kubectl top pods -l app=django-messaging

echo -e "\nNODE RESOURCES:"
kubectl top nodes

echo -e "\nFinal status report:"
kubectl get deployment django-messaging-app -o wide
kubectl get hpa 2>/dev/null || echo "No HPA configured"