project_id         = "" # TODO
region             = "us-central1" # cheapest :D
zones              = ["us-central1-c"]
gke_num_nodes      = 1
machine_type       = "custom-4-4096" # 4vCPU & 4GB RAM
kubernetes_version = "1.19"
release_channel    = "RAPID"
master_authorized_cidr_blocks = [""] # TODO
