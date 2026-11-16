Write-Host "=== 1. GIT & GITHUB CI ===" -ForegroundColor Cyan
git status -s
git log -1 --oneline
gh run list --limit 3

Write-Host "`n=== 2. KIND CLUSTER & ARGOCD ===" -ForegroundColor Cyan
kubectl config use-context kind-innovate
kubectl get nodes
kubectl get applications -n argocd

Write-Host "`n=== 3. PODS ACROSS ENVIRONMENTS ===" -ForegroundColor Cyan
kubectl get pods -n dev -n staging -n prod

Write-Host "`n=== 4. LIVE ENDPOINT & DB!HEALTH ===" -ForegroundColor Cyan
$pfJob = $null
if (-not (Get-NetTCPConnection -LocalPort 8086 -ErrorAction SilentlyContinue)) {
    $pfJob = Start-Job -ScriptBlock { kubectl port-forward --address 127.0.0.1 svc/ingress-nginx-controller -n ingress-nginx 8086:80 }
    Start-Sleep -Seconds 3
}

try {
    Write-Host "Dev (/db-test):     " -NoNewline; curl.exe -s http://localhost:8086/db-test
    Write-Host "Dev (/incidents):   " -NoNewline; curl.exe -s http://localhost:8086/api/incidents
    Write-Host "Staging (/health):  " -NoNewline; curl.exe -s -H "Host: staging.emergencydashboard.online" http://localhost:8086/health
    Write-Host "Prod (/health):     " -NoNewline; curl.exe -s -H "Host: prod.emergencydashboard.online" http://localhost:8086/health
} finally {
    if ($pfJob) {
        Stop-Job $pfJob
        Remove-Job $pfJob
    }
}
