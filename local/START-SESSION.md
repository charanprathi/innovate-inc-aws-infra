# Session Quick-Start Guide

Quick commands to resume working on the `innovate` Kind cluster, ArgoCD apps, and local/ngrok ingress.

---

## 1. Verify Cluster & ArgoCD Health (Terminal 1)

```powershell
kubectl config use-context kind-innovate
kubectl get nodes
kubectl get applications -n argocd
kubectl get pods -n dev -n staging -n prod
```

---

## 2. Start Local Ingress Port-Forward (Terminal 2)

```powershell
kubectl port-forward --address 0.0.0.0 svc/ingress-nginx-controller -n ingress-nginx 8086:80
```

---

## 3. Start External ngrok Tunnel (Terminal 3 — Optional)

```powershell
ngrok http 8086
```

---

## 4. Build, Deploy & Promote Changes (Terminal 1)

```powershell
# Deploy to dev (default)
.\local\deploy-local.ps1

# Promote to staging and prod
.\local\deploy-local.ps1 -Env staging
.\local\deploy-local.ps1 -Env prod
```

---

## 5. Quick Endpoint Checks

```powershell
# Dev (default route)
curl.exe -s http://localhost:8086/db-test
curl.exe -s http://localhost:8086/api/incidents

# Staging & Prod (via Host header)
curl.exe -s -H "Host: staging.emergencydashboard.online" http://localhost:8086/api/incidents
curl.exe -s -H "Host: prod.emergencydashboard.online" http://localhost:8086/api/incidents
```
