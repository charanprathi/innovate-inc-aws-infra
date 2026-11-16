param(
    [ValidateSet("dev", "staging", "prod")]
    [string]$Env = "dev"
)

$ErrorActionPreference = "Stop"
$tag = if ($Env -eq "dev") { "innovate-app:local" } else { "innovate-app:$Env" }

Write-Host "1/3 Building $tag..." -ForegroundColor Cyan
docker build -t $tag ./app

Write-Host "2/3 Loading $tag into Kind cluster 'innovate'..." -ForegroundColor Cyan
kind load docker-image $tag --name innovate

Write-Host "3/3 Restarting deployment/innovate-app in namespace '$Env'..." -ForegroundColor Cyan
kubectl rollout restart deployment/innovate-app -n $Env
kubectl rollout status deployment/innovate-app -n $Env

kubectl get pods -n $Env
