variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "cluster_name" {
  type    = string
  default = "jizt-cluster"
}

variable "public_subnet_count" {
  description = "Number of public subnets."
  type        = number
  default     = 2
}

variable "private_subnet_count" {
  description = "Number of private subnets."
  type        = number
  default     = 2
}

variable "base_cidr_block" {
  description = "Base CIDR block to be used in our VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_prefix_extension" {
  type        = number
  description = "CIDR block bits extension to calculate CIDR blocks of each subnetwork."
  default     = 4
}

variable "zone_offset" {
  type        = number
  description = "CIDR block bits extension offset to calculate Public subnets, avoiding collisions with Private subnets."
  default     = 8
}

variable "k8s_api_public_cidrs" {
  description = "Cidr blocks that can access public endpoint for Kubernetes API."
  type        = list(string)
  sensitive   = true
}

variable "ec2_instance_type" {
  description = "AWS EC2 instance type."
  type        = string
  default     = "t4g.medium"
}

variable "asg_desired_capacity" {
  description = "Desired number of EC2 instances in each of the cluster worker groups."
  type        = number
  default     = 1
}

variable "asg_max_size" {
  description = "Maximum number of EC2 instances in each of the cluster worker groups."
  type        = number
  default     = 1
}

variable "asg_min_size" {
  description = "Minimum number of EC2 instances in each of the cluster worker groups."
  type        = number
  default     = 1
}
