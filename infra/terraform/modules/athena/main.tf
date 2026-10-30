variable "name" { type = string }
variable "results_bucket" { type = string }
variable "database_name" { type = string }
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

locals {
  gold_queries = {
    vehicle_trip_summary = <<-SQL
      SELECT vehicle_id, trip_id, event_date, count(*) AS events,
        avg(speed_kph) AS avg_speed_kph, min(battery_soc) AS min_battery_soc,
        avg(energy_consumption_kwh) AS avg_energy_consumption_kwh,
        avg(range_estimate_km) AS avg_range_estimate_km
      FROM ${var.database_name}.telemetry_silver
      WHERE data_quality_flag = 'VALID'
      GROUP BY 1, 2, 3
    SQL
    connectivity_summary = <<-SQL
      SELECT event_date, scenario, route_segment, network_type, count(*) AS events, avg(latency_ms) AS avg_latency_ms,
        approx_percentile(latency_ms, 0.95) AS p95_latency_ms,
        avg(connection_stability_score) AS avg_connection_stability_score,
        avg(offline_duration_s) AS avg_offline_duration_s,
        avg(reconnection_count) AS avg_reconnection_count,
        avg(packet_loss_pct) AS avg_packet_loss_pct,
        sum(bytes_buffered) AS buffered_bytes,
        avg(sync_duration_ms) AS avg_sync_duration_ms
      FROM ${var.database_name}.telemetry_silver
      GROUP BY 1, 2, 3, 4
    SQL
    hmi_warning_performance = <<-SQL
      SELECT event_date, warning_level, approx_percentile(warning_latency_ms, 0.50) AS p50_warning_latency_ms,
        approx_percentile(warning_latency_ms, 0.95) AS p95_warning_latency_ms,
        avg(CASE WHEN object_detected AND warning_displayed_at IS NULL THEN 1.0 ELSE 0.0 END) AS missing_warning_rate,
        avg(driver_response_time_ms) AS avg_driver_response_time_ms
      FROM ${var.database_name}.telemetry_silver
      GROUP BY 1, 2
    SQL
    sensor_quality = <<-SQL
      SELECT event_date, data_quality_flag, count(*) AS records,
        avg(late_arrival_seconds) AS avg_late_arrival_seconds,
        avg(processing_latency_ms) AS avg_processing_latency_ms
      FROM ${var.database_name}.telemetry_silver
      GROUP BY 1, 2
    SQL
  }
}

resource "aws_athena_named_query" "gold" {
  for_each  = local.gold_queries
  name      = "${var.name}-${each.key}"
  database  = var.database_name
  workgroup = aws_athena_workgroup.this.name
  query     = each.value
}
output "workgroup_name" { value = aws_athena_workgroup.this.name }
