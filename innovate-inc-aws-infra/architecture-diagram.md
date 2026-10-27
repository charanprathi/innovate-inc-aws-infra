# Comprehensive System Architecture & Workflow Diagram

Add this complete Mermaid diagram block to your `README.md` to visually document the entire end-to-end platform architecture, network peering, and deployment pipeline.

```mermaid
flowchart TB
    subgraph external ["Edge & User Access"]
        user["User / Browser"]
        dns["Route 53<br/>emergencydashboard.online<br/>(A Alias to ALB)"]
    end

    subgraph cicd ["CI/CD & GitOps Flow"]
        dev["Developer"] -->|"git push to main<br/>(app/**)"| gh["GitHub Repository"]
        gh -->|"Triggers Workflow"| ga["GitHub Actions"]
        subgraph pipeline ["Build Pipeline"]
            s1["Checkout Code"] --> s2["Configure AWS Credentials<br/>(Scoped ECR-only IAM User)"]
            s2 --> s3["Login to Amazon ECR"]
            s3 --> s4["Build & Trivy Vulnerability Scan"]
            s4 --> s5["Push Docker Image to ECR<br/>(Tags: commit SHA & latest)"]
        end
        ga --> pipeline
    end

    subgraph aws ["AWS Account (us-east-1)"]
        subgraph foundation ["Phase 1: Foundation & Governance"]
            trail["CloudTrail<br/>(Multi-region + S3)"]
            config["AWS Config<br/>(Recorder & Channel)"]
            budgets["AWS Budgets<br/>($500 Limit & Alerts)"]
        end

        subgraph prodvpc ["Prod VPC (10.0.0.0/16)"]
            alb["Application Load Balancer<br/>(Public Subnets, ACM Cert, HTTP->HTTPS)"]
            subgraph eks ["EKS Cluster: innovate-inc-cluster (Fargate Only)"]
                lbc["AWS Load Balancer Controller<br/>(kube-system, IRSA)"]
                subgraph ns_dev ["Namespace: dev"]
                    pods["Flask App Pods x2<br/>(gunicorn, port 5000)"]
                end
                subgraph ns_argocd ["Namespace: argocd"]
                    argocd["ArgoCD & AppSet Controller<br/>(GitOps Delivery)"]
                end
            end
        end

        subgraph devvpc ["Dev VPC (10.1.0.0/16)"]
            rds[("RDS PostgreSQL<br/>innovate-dev-db<br/>(Private Subnets)"]]
        end

        subgraph stagingvpc ["Staging VPC (10.2.0.0/16)"]
            staging_net["Networking Only<br/>(Subnets & NAT Gateway)"]
        end
    end

    user -->|"HTTPS 443"| dns
    dns --> alb
    alb -->|"IP Target Type"| pods
    lbc -.->|"Manages"| alb
    pods -->|"VPC Peering & TCP 5432<br/>(Prod CIDR 10.0.0.0/16 allowed in RDS SG)"| rds
    s5 -.->|"Intended GitOps Sync"| argocd
    argocd -.-> pods
```