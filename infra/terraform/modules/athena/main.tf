variable "name" { type = string }
variable "results_bucket" { type = string }
variable "tags" { type = map(string) }
resource "aws_athena_workgroup" "this" {
  name = "${var.name}-analytics"
  configuration {
    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true
    result_configuration {
      output_location = "s3://${var.results_bucket}/"
      encryption_configuration { encryption_option = "SSE_S3" }
    }
  }
  tags = var.tags
}
output "workgroup_name" { value = aws_athena_workgroup.this.name }
