terraform {
  backend "s3" {
    bucket         = "innovate-inc-tfstate-811165582680"
    key            = "ingress/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "innovate-inc-tflock"
    encrypt        = true
  }
}
