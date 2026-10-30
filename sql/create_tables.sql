-- Run after Terraform has catalogued the Silver Parquet prefix.
CREATE OR REPLACE VIEW drivesense_dev_catalog.vehicle_trip_summary AS
SELECT vehicle_id, trip_id, date(event_timestamp) AS trip_date,
       count(*) AS events, avg(speed_kph) AS avg_speed_kph,
       min(battery_soc) AS min_battery_soc
FROM drivesense_dev_catalog.telemetry_silver
WHERE data_quality_flag = 'VALID'
GROUP BY 1, 2, 3;

