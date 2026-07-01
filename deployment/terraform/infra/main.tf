resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = merge(var.common_tags, {
    Name = "Main VPC"
  })
}

resource "aws_internet_gateway" "igw" {
  tags = merge(var.common_tags, {
    Name = "Main Internet Gateway"
  })
}

resource "aws_internet_gateway_attachment" "igw_attach" {
  internet_gateway_id = aws_internet_gateway.igw.id
  vpc_id              = aws_vpc.main.id
}


resource "aws_route_table" "vpc_rt" {
  vpc_id = aws_vpc.main.id
  tags = merge(var.common_tags, {
    Name = "VPC Route Table"
  })
}

resource "aws_route" "route" {
  route_table_id         = aws_route_table.vpc_rt.id
  gateway_id             = aws_internet_gateway.igw.id
  destination_cidr_block = local.all_routes_open
}

resource "aws_subnet" "public_subnet" {
  for_each          = { for i in range(var.num_subnets) : "public${i}" => i }
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, each.value)
  availability_zone = local.azs[each.value % length(local.azs)]

  tags = merge(var.common_tags, {
    Name = "Public subnet ${each.key}"
  })
}

resource "aws_route_table_association" "public_rt_subnet_association" {
  for_each       = aws_subnet.public_subnet
  route_table_id = aws_route_table.vpc_rt.id
  subnet_id      = aws_subnet.public_subnet[each.key].id
}