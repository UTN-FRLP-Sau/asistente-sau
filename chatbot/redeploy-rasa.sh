#!/bin/bash

echo "Eliminando deployments de Rasa..."

kubectl delete deployment rasa-1worker --ignore-not-found
kubectl delete deployment rasa-2workers --ignore-not-found

echo "Aplicando archivos de deployment para Rasa..."

kubectl apply -f deployment/rasa-deployment-1worker.yaml
kubectl apply -f deployment/rasa-deployment-2worker.yaml
kubectl apply -f deployment/rasa-service.yaml

echo "Esperando rollout de deployments..."
kubectl rollout status deployment/rasa-1worker
kubectl rollout status deployment/rasa-2workers

echo "Rasa redeploy completado ✅"

