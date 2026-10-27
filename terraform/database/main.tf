provider "aws" {
  region = "us-east-1"
}

resource "aws_db_subnet_group" "dev_db_subnets" {
  name       = "innovate-dev-db-subnets"
  subnet_ids = ["subnet-022604cfcaf09ffdf", "subnet-0cefa41f7d80dbb9c"]
}

resource "aws_security_group" "dev_db_sg" {
  name        = "innovate-dev-db-sg"
  description = "Allow PostgreSQL traffic from Dev EKS Namespace"
  vpc_id      = "vpc-04d75110c4d4f831a"

  ingress {
    description = "PostgreSQL access from EKS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.1.0.0/16"] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "dev_postgres" {
  identifier             = "innovate-dev-db"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  
  db_name                = "innovate_dev"
  username               = "dbadmin"
  password               = "DevPassword2026!" 
  
  vpc_security_group_ids = [aws_security_group.dev_db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.dev_db_subnets.name 
  
  skip_final_snapshot    = true
  publicly_accessible    = false
}
