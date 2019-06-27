module "aws" {
  source          = "astronomer/astronomer-aws/aws"
  version         = "1.0.8"
  #source          = "./terraform-aws-astronomer-aws"
  deployment_id   = var.deployment_id
  admin_email     = var.email
  route53_domain  = var.route53_domain
  vpc_id          = var.vpc_id
  private_subnets = var.private_subnets
  enable_bastion = var.enable_bastion
  public_subnets = var.public_subnets
  # It makes the installation easier to leave
  # this public, then just flip it off after
  # everything is deployed.
  # Otherwise, you have to deal with a bastion
  # and proxy settings.
  management_api  = var.management_api
}

# install tiller, which is the server-side component
# of Helm, the Kubernetes package manager
module "system_components" {
  source       = "astronomer/astronomer-system-components/kubernetes"
  version      = "0.0.3"
  enable_istio = "false"
}

module "astronomer" {
  source  = "astronomer/astronomer/kubernetes"
  version = "1.0.1"
  cluster_type          = "private"
  private_load_balancer = true
  base_domain           = module.aws.base_domain
  db_connection_string  = module.aws.db_connection_string
  tls_cert              = module.aws.tls_cert
  tls_key               = module.aws.tls_key
}

