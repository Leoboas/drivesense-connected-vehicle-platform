SELECT event_date, data_quality_flag, count(*) AS records
FROM drivesense_dev_catalog.telemetry_silver GROUP BY 1, 2 ORDER BY 1, 2;

