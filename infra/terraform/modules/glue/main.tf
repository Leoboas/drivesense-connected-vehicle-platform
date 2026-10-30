variable "name" { type = string }
variable "data_bucket" { type = string }
variable "silver_prefix" { type = string }
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
  glue_version       = "4.0"
  max_retries        = 1
  worker_type        = "G.1X"
  number_of_workers  = 2
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

resource "aws_glue_catalog_table" "telemetry_silver" {
  name          = "telemetry_silver"
  database_name = aws_glue_catalog_database.this.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    "EXTERNAL"                                = "TRUE"
    "classification"                          = "parquet"
    "projection.enabled"                      = "true"
    "projection.event_date.type"              = "date"
    "projection.event_date.range"             = "2026-01-01,2026-12-31"
    "projection.event_date.format"            = "yyyy-MM-dd"
    "projection.event_date.interval"          = "1"
    "projection.event_date.interval.unit"     = "DAYS"
    "storage.location.template"               = "s3://${var.data_bucket}/${var.silver_prefix}event_date=$${event_date}/"
  }
  partition_keys {
    name = "event_date"
    type = "date"
  }
  storage_descriptor {
    location      = "s3://${var.data_bucket}/${var.silver_prefix}"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    ser_de_info {
      name                  = "parquet"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
    columns {
      name = "event_id"
      type = "string"
    }
    columns {
      name = "vehicle_id"
      type = "string"
    }
    columns {
      name = "trip_id"
      type = "string"
    }
    columns {
      name = "timestamp"
      type = "string"
    }
    columns {
      name = "event_timestamp"
      type = "timestamp"
    }
    columns {
      name = "latitude"
      type = "double"
    }
    columns {
      name = "longitude"
      type = "double"
    }
    columns {
      name = "speed_kph"
      type = "double"
    }
    columns {
      name = "battery_soc"
      type = "double"
    }
    columns {
      name = "network_type"
      type = "string"
    }
    columns {
      name = "signal_dbm"
      type = "double"
    }
    columns {
      name = "latency_ms"
      type = "double"
    }
    columns {
      name = "connection_state"
      type = "string"
    }
    columns {
      name = "proximity_front_cm"
      type = "double"
    }
    columns {
      name = "object_detected"
      type = "boolean"
    }
    columns {
      name = "warning_generated_at"
      type = "string"
    }
    columns {
      name = "warning_displayed_at"
      type = "string"
    }
    columns {
      name = "schema_version"
      type = "string"
    }
    columns {
      name = "event_rank"
      type = "int"
    }
    columns {
      name = "data_quality_flag"
      type = "string"
    }
    columns {
      name = "warning_latency_ms"
      type = "double"
    }
    columns {
      name = "connection_stability_score"
      type = "int"
    }
  }
  depends_on = [aws_glue_job.telemetry_etl]
}
output "database_name" { value = aws_glue_catalog_database.this.name }
output "silver_table_name" { value = aws_glue_catalog_table.telemetry_silver.name }
