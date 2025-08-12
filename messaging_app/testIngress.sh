#!/bin/bash
# Add to your hosts file
echo "$(minikube ip) messaging-app.local" | sudo tee -a /etc/hosts

# Test in browser
http://messaging-app.local/
http://messaging-app.local/api/
http://messaging-app.local/admin/