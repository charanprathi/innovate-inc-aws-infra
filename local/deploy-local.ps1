$ErrorActionPreference = "Stop"

Write-Host "1/3 Building innovate-app:local..." -ForegroundColor Cyan
docker build -t innovate-app:local ./app

Write-Host "2/3 Loading image into Kind cluster 'innovate'..." -ForegroundColor Cyan
kind load docker-image innovate-app:local --name innovate

Write-Host "3/3 Restarting deployment/innovate-app in namespace 'dev'..." -ForegroundColor Cyan
kubectl rollout restart deployment/innovate-app -n dev
kubectl rollout status deployment/innovate-app -n dev

kubectl get pods -n dev
