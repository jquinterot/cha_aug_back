#!/bin/bash

# Apply all Kubernetes manifests
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml -n chat-aug
kubectl apply -f deployment.yaml -n chat-aug
kubectl apply -f service.yaml -n chat-aug
kubectl apply -f ingress.yaml -n chat-aug

# Check the status of the deployment
echo "Checking deployment status..."
kubectl get pods -n chat-aug

echo "Use these commands to monitor your deployment:"
echo "kubectl get pods -n chat-aug"
echo "kubectl get svc -n chat-aug"
echo "kubectl get ingress -n chat-aug"

echo "To access your application, add an entry to your /etc/hosts file:"
echo "<YOUR_NODE_IP> chat.yourdomain.com"

# If you need to debug
echo "\nDebugging commands:"
echo "kubectl logs -f <pod-name> -n chat-aug"
echo "kubectl describe pod <pod-name> -n chat-aug"
