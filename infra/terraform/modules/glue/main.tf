variable "name" { type = string }
variable "data_bucket" { type = string }
variable "glue_role_arn" { type = string }
variable "tags" { type = map(string) }
resource "aws_glue_catalog_database" "this" {
  name = replace("${var.name}_catalog", "-", "_")
}
resource "aws_glue_crawler" "bronze" {
  name = "${var.name}-bronze-crawler"
  role = var.glue_role_arn
  database_name = aws_glue_catalog_database.this.name
  s3_target { path = "s3://${var.data_bucket}/bronze/" }
  tags = var.tags
}
resource "aws_glue_job" "telemetry_etl" {
  name = "${var.name}-telemetry-etl"
  role_arn = var.glue_role_arn
  glue_version = "4.0"
  max_retries = 1
  command {
    name            = "glueetl"
    script_location = "s3://${var.data_bucket}/artifacts/telemetry_etl.py"
    python_version  = "3"
  }
  default_arguments = {
    "--job-language"                      = "python"
    "--enable-metrics"                     = "true"
    "--enable-continuous-cloudwatch-log"   = "true"
    "--enable-spark-ui"                    = "true"
    "--spark-event-logs-path"              = "s3://${var.data_bucket}/spark-event-logs/"
  }
  tags = var.tags
}
output "database_name" { value = aws_glue_catalog_database.this.name }
