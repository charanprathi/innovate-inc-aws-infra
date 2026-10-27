data "aws_availability_zones" "available" {
  state = "available"
}

module "dev_vpc" {
  source                = "./modules/vpc"
  name                  = "dev"
  cidr_block            = "10.1.0.0/16"
  azs                   = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnet_cidrs   = ["10.1.0.0/24", "10.1.1.0/24"]
  private_subnet_cidrs  = ["10.1.10.0/24", "10.1.11.0/24"]
}

module "staging_vpc" {
  source                = "./modules/vpc"
  name                  = "staging"
  cidr_block            = "10.2.0.0/16"
  azs                   = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnet_cidrs   = ["10.2.0.0/24", "10.2.1.0/24"]
  private_subnet_cidrs  = ["10.2.10.0/24", "10.2.11.0/24"]
}

module "prod_vpc" {
  source                = "./modules/vpc"
  name                  = "prod"
  cidr_block            = "10.0.0.0/16"
  azs                   = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnet_cidrs   = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnet_cidrs  = ["10.0.10.0/24", "10.0.11.0/24"]
}
