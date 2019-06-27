variable "route53_domain" {
  description = "The name of your public route53 hosted zone, does not include a trailing dot. Should match the domain. This is used to generate a certificate with let's encrypt"
  type = string
}

variable "management_api" {
  description = "'public' or 'private', this will enable / disable the public EKS endpoint. It's easier to deploy the platform from scratch if you leave it public. Then you can just toggle if off in the console for better security."
  type = string
}

variable "email" {
  description = "Email address to use when requesting the let's encrypt TLS certificate"
  type = string
}

variable "vpc_id" {
  description = "The VPC ID in which your subnets are located"
  type = string
}

variable "deployment_id" {
  description = "A short, letters-only string to identify your deployment, and to prefix some AWS resources. We recommend 'astro'."
  type = string
}

variable "private_subnets" {
  description = "list of subnet ids, should be private subnets in different AZs"
  type = list(string)
}

variable "public_subnets" {
  default = []
  description = "list of subnet ids, you probably only need one. This is for the bastion host, if the bastion is diabled, you don't need this."
  type = list(string)
}

variable "aws_region" {
  default = "us-west-2"
  type = string
}

variable "acme_server" {
  description = "Endpoint to use for generating the let's encrypt TLS certificate. Defaults to the production endpoint"
  default = "https://acme-v02.api.letsencrypt.org/directory"
  # default = "https://acme-staging-v02.api.letsencrypt.org/directory"
  type = string
}

variable "enable_bastion" {
  description = "Launch a bastion in a public subnet? For this to work, you must include 1 subnet id in the public_subets variable"
  type = bool
}
