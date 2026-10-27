terraform {
  backend "s3" {
    bucket         = "innovate-inc-tfstate-811165582680"
    key            = "foundation/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "innovate-inc-tflock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
