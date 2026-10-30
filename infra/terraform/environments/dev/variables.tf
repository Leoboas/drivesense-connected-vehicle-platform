variable "aws_region" {
  type    = string
  default = "us-east-1"
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
