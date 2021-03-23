terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0.0"
    }
  }
  required_version = "~> 0.14"
}

provider "aws" {
  region = var.region
}

data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}

data "aws_availability_zones" "available" {
}

# terraform state rm module.eks.kubernetes_config_map.aws_auth
provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name = "${var.cluster_name}-vpc"
  cidr = var.base_cidr_block
  azs  = data.aws_availability_zones.available.names
  private_subnets = [
    # this loop will create a one-line list as ["10.0.0.0/20", "10.0.16.0/20", "10.0.32.0/20", ...]
    # with a length depending on how many Zones are available
    for zone_id in data.aws_availability_zones.available.zone_ids :
    cidrsubnet(var.base_cidr_block, var.subnet_prefix_extension, tonumber(substr(zone_id, length(zone_id) - 1, 1)) - 1)
  ]
  public_subnets = [
    # this loop will create a one-line list as ["10.0.128.0/20", "10.0.144.0/20", "10.0.160.0/20", ...]
    # with a length depending on how many Zones are available
    # there is a zone Offset variable, to make sure no collisions are present with private subnet blocks
    for zone_id in data.aws_availability_zones.available.zone_ids :
    cidrsubnet(var.base_cidr_block, var.subnet_prefix_extension, tonumber(substr(zone_id, length(zone_id) - 1, 1)) + var.zone_offset - 1)
  ]
  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false
  enable_dns_hostnames   = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "14.0.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.19" # Kubernetes version

  cluster_endpoint_private_access      = true
  cluster_endpoint_public_access_cidrs = var.k8s_api_public_cidrs
  subnets                              = module.vpc.private_subnets
  vpc_id                               = module.vpc.vpc_id

  worker_groups = [
    {
      instance_type        = var.ec2_instance_type
      asg_desired_capacity = var.asg_desired_capacity
      asg_max_size         = var.asg_max_size
      asg_min_size         = var.asg_min_size
    }
  ]

  # !!! Change to "gp3" when it is available
  # https://github.com/terraform-aws-modules/terraform-aws-eks/issues/1205
  workers_group_defaults = {
    root_volume_type = "gp2"
  }
}
