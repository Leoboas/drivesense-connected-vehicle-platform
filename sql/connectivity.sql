WITH daily AS (
  SELECT vehicle_id, event_date, avg(latency_ms) AS avg_latency_ms,
    approx_percentile(latency_ms, 0.95) AS p95_latency_ms,
    sum(CASE WHEN connection_state = 'OFFLINE' THEN 1 ELSE 0 END) AS offline_events
  FROM drivesense_silver.telemetry
  WHERE event_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31' -- partition pruning
  GROUP BY 1, 2
)
SELECT *, rank() OVER (PARTITION BY event_date ORDER BY avg_latency_ms DESC) AS latency_rank FROM daily;

