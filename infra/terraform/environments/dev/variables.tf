variable "aws_region" {
  type    = string
  default = "us-east-1"
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
