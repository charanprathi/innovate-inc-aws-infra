resource "aws_vpc_peering_connection" "prod_to_dev" {
  vpc_id      = "vpc-05a489f2079aa8085"
  peer_vpc_id = "vpc-04d75110c4d4f831a"
  auto_accept = true

  tags = {
    Name = "prod-to-dev-peering"
  }
}

data "aws_route_table" "prod_private" {
  filter {
    name   = "tag:Name"
    values = ["prod-private-rt"]
  }
}

data "aws_route_table" "dev_private" {
  filter {
    name   = "tag:Name"
    values = ["dev-private-rt"]
  }
}

resource "aws_route" "prod_to_dev" {
  route_table_id            = data.aws_route_table.prod_private.id
  destination_cidr_block    = "10.1.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
}

resource "aws_route" "dev_to_prod" {
  route_table_id            = data.aws_route_table.dev_private.id
  destination_cidr_block    = "10.0.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
}
