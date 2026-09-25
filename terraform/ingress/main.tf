terraform {
  required_providers {
    aws  = { source = "hashicorp/aws", version = "~> 5.0" }
    helm = { source = "hashicorp/helm", version = "~> 2.0" }
    tls  = { source = "hashicorp/tls", version = "~> 4.0" }
  }
}

provider "aws" { region = "us-east-1" }
provider "helm" {
  kubernetes { config_path = "~/.kube/config" }
}

# 1. Automatically fetch your existing EKS cluster
data "aws_eks_cluster" "eks" {
  name = "innovate-inc-cluster"
}

# 2. Fetch the TLS certificate thumbprint for the OIDC provider
data "tls_certificate" "eks" {
  url = data.aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

# 3. Create the missing IAM OIDC Identity Provider
resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = data.aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

# 4. Create the IAM Role for the Load Balancer Controller
module "lb_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.30"

  role_name                              = "innovate-dev-alb-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = aws_iam_openid_connect_provider.eks.arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

# 5. Install the AWS Load Balancer Controller via Helm
resource "helm_release" "alb_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"

  set {
    name  = "clusterName"
    value = data.aws_eks_cluster.eks.name
  }

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.lb_role.iam_role_arn
  }
  
  set {
    name  = "vpcId"
    value = "vpc-04d75110c4d4f831a" 
  }
  
  set {
    name  = "region"
    value = "us-east-1"
  }
}
