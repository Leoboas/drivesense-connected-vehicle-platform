terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" { region = var.aws_region }

locals { name = "drivesense-${var.environment}" }

module "s3" {
  source = "../../modules/s3"
  name   = local.name
  tags   = var.tags
}
module "iam" {
  source     = "../../modules/iam"
  name       = local.name
  bucket_arn = module.s3.data_bucket_arn
  tags       = var.tags
}
module "glue" {
  source        = "../../modules/glue"
  name          = local.name
  data_bucket   = module.s3.data_bucket_id
  silver_prefix = var.silver_prefix
  glue_role_arn = module.iam.glue_role_arn
  tags          = var.tags
}
module "athena" {
  source         = "../../modules/athena"
  name           = local.name
  results_bucket = module.s3.results_bucket_id
  database_name  = module.glue.database_name
  tags           = var.tags
}

