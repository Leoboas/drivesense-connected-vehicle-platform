SELECT event_date, data_quality_flag, count(*) AS records
FROM drivesense_silver.telemetry GROUP BY 1, 2 ORDER BY 1, 2;

