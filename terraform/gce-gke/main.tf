# https://github.com/terraform-google-modules/terraform-google-kubernetes-engine/blob/master/modules/private-cluster/README.md
# https://registry.terraform.io/modules/terraform-google-modules/kubernetes-engine/google/latest
# https://registry.terraform.io/modules/terraform-google-modules/network/google/latest

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.60.0"
    }
    # kubernetes = {
    #   source  = "hashicorp/kubernetes"
    #   version = "2.0.3"
    # }
  }
  required_version = "~> 0.14"
}

data "google_client_config" "default" {}

provider "kubernetes" {
  load_config_file       = false
  host                   = "https://${module.gke.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.ca_certificate)
}

module "gcp-network" {
  source       = "terraform-google-modules/network/google"
  version = "~> 3.0"
  project_id   = var.project_id
  network_name = var.network

  subnets = [
    {
      subnet_name           = var.subnetwork
      subnet_ip             = "10.100.0.0/18"
      subnet_region         = var.region
      subnet_private_access = "true"
    },
  ]

  secondary_ranges = {
    "${var.subnetwork}" = [
      {
        range_name    = var.ip_range_pods_name
        ip_cidr_range = "10.24.0.0/14"
      },
      {
        range_name    = var.ip_range_services_name
        ip_cidr_range = "10.28.0.0/20"
      },
    ]
  }
}

data "google_compute_subnetwork" "subnetwork" {
  name       = var.subnetwork
  project    = var.project_id
  region     = var.region
  depends_on = [module.gcp-network]
}

module "gke" {
  source                     = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  project_id                 = var.project_id
  name                       = "${var.global_name}-cluster"
  description                = "Jizt production cluster."
  kubernetes_version         = var.kubernetes_version
  release_channel            = var.release_channel
  regional                   = false
  region                     = var.region
  zones                      = var.zones
  network                    = module.gcp-network.network_name
  subnetwork                 = module.gcp-network.subnets_names[0]
  ip_range_pods              = var.ip_range_pods_name
  ip_range_services          = var.ip_range_services_name
  http_load_balancing        = true  # required to use GC Load Balancer with Ingress
  enable_shielded_nodes      = true
  horizontal_pod_autoscaling = false
  network_policy             = false
  enable_private_endpoint    = false
  remove_default_node_pool   = true
  create_service_account     = true
  grant_registry_access      = true

  master_authorized_networks = [
    {
      cidr_block   = var.master_authorized_cidr_blocks[0]
      display_name = "authorized_cidr_block"
    },
  ]

  node_pools = [
    {
      name                              = "${var.global_name}-pool"
      autoscaling                       = false
      preemptible                       = false
      machine_type                      = var.machine_type
      node_count                        = var.gke_num_nodes
      local_ssd_count                   = 0
      disk_size_gb                      = 30
      disk_type                         = "pd-standard"
      image_type                        = "cos_containerd"
      auto_repair                       = true
      auto_upgrade                      = true
      initial_node_count                = var.gke_num_nodes
      disable_legacy_metadata_endpoints = true
    },
  ]

  node_pools_oauth_scopes = {
    all = []

    default-node-pool = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  node_pools_labels = {
    all = {}

    default-node-pool = {
      default-node-pool = true
    }
  }

  node_pools_metadata = {
    all = {}

    default-node-pool = {
      node-pool-metadata-custom-value = "${var.global_name}-pool"
    }
  }

  node_pools_tags = {
    all = []

    default-node-pool = [
      "default-node-pool",
    ]
  }
}
