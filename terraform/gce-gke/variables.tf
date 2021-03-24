variable "global_name" {
  description = "Name to use for the cluster and other resources."
  type        = string
  default     = "jizt"
}

variable "project_id" {
  description = "GCE Project ID."
  type        = string
}

variable "gke_username" {
  description = "GKE username."
  type        = string
  sensitive   = true
}

variable "gke_password" {
  description = "GKE password."
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Cluster region."
  type        = string
  default     = "us-central1"
}

variable "zones" {
  description = "Cluster zone."
  type        = list(string)
  default     = ["us-central1-c"]
}

variable "network" {
  description = "The VPC network created to host the cluster in."
  type = string
  default     = "gke-network"
}

variable "subnetwork" {
  description = "The subnetwork created to host the cluster in."
  type = string
  default     = "gke-subnet"
}

variable "ip_range_pods_name" {
  description = "The secondary ip range to use for pods."
  type = string
  default     = "ip-range-pods"
}

variable "ip_range_services_name" {
  description = "The secondary ip range to use for services."
  type = string
  default     = "ip-range-svc"
}

variable "master_authorized_cidr_blocks" {
  description = "Authorized CIDR blocks for external access to the cluster."
  type        = list(string)
}

variable "gke_num_nodes" {
  description = "Number of GKE nodes in the cluster."
  type        = number
  default     = 1
}

variable "machine_type" {
  description = "Node machine type."
  type        = string
  default     = "e2-standard-4"
}

variable "kubernetes_version" {
  description = "Kubernetes version."
  type        = string
  default     = "1.19"
}

variable "release_channel" {
  description = "Release channel of the cluster."
  type        = string
  default     = "REGULAR"
}
