# Innovate Inc – Local GitOps Architecture

```mermaid
flowchart TB
    Dev[(Developer / Git Push to main)] -->|Triggers CI| GHA[GitHub Actions<br>build-and-push.yml]
    GHA -->|Docker Build + Security Scan| Trivy[Trivy Vulnerability Scanner]
    
    Dev -->|Local Build & Load| Script[local/deploy-local.ps1]
    Script -->|docker build + kind load| Node[Kind Node: innovate-control-plane]

    GitRepo[(GitHub: charanprathi/innovate-inc-aws-infra<br>local/apps/*)] -->|Polls & Auto-Syncs| Argo[ArgoCD GitOps Controller<br>selfHeal + prune]
    Argo -->|Deploys Manifests| Node

    User[(Browser / curl / ngrok Tunnel)] -->|localhost:8086| PF[kubectl port-forward<br>8086 -> 80]
    PF --> Ingress[Ingress-NGINX Controller]

    subgraph Cluster [Kind Kubernetes Cluster: innovate]
        Ingress -->|Default / emergencydashboard.online| DevPod
        Ingress -->|Host: staging.emergencydashboard.online| StgPod
        Ingress -->|Host: prod.emergencydashboard.online| ProdPods

        subgraph NS_DEV [Namespace: dev]
            DevPod[innovate-app<br>1 Replica] --> DevDB["PostgreSQL 16<br>innovate_dev"]
        end

        subgraph NS_STG [Namespace: staging]
            StgPod[innovate-app<br>1 Replica] --> StgDB["PostgreSQL 16<br>innovate_staging"]
        end

        subgraph NS_PRD [Namespace: prod]
            ProdPods[innovate-app<br>2 Replicas] --> ProdDB"PostgreSQL 16<br>innovate_prod"]
        end
    end
```
