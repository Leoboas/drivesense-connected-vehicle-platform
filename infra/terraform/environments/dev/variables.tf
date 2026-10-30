variable "aws_region" {
  type        = string
  description = "Project selected Region. DriveSense resources must remain in us-east-2."
  default     = "us-east-2"

  validation {
    condition     = var.aws_region == "us-east-2"
    error_message = "DriveSense project resources must be planned and applied in us-east-2."
  }
}
variable "silver_prefix" {
  type        = string
  description = "S3 prefix containing the partitioned Silver Parquet dataset to catalogue."
  default     = "silver/cloud-multimedia-20261030-001/"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "tags" {
  type = map(string)
  default = {
    Project = "DriveSense", Environment = "dev", ManagedBy = "Terraform", Owner = "platform"
  }
}
