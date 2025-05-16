#!/bin/bash

echo "Eliminando deployment de Redis..."

kubectl delete deployment redis --ignore-not-found

echo "Aplicando archivos de deployment para Redis..."

kubectl apply -f deployment/redis-deployment.yaml
kubectl apply -f deployment/redis-service.yaml

echo "Esperando rollout de deployment..."
kubectl rollout status deployment/redis

echo "Redis redeploy completado ✅"

