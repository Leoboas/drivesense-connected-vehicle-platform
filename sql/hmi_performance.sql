SELECT event_date, approx_percentile(warning_latency_ms, 0.50) AS p50_ms,
  approx_percentile(warning_latency_ms, 0.95) AS p95_ms,
  approx_percentile(warning_latency_ms, 0.99) AS p99_ms,
  avg(CASE WHEN object_detected AND warning_displayed_at IS NULL THEN 1.0 ELSE 0.0 END) AS missing_warning_rate
FROM drivesense_silver.telemetry GROUP BY 1;

