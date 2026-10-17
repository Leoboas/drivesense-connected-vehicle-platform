# Data model

## Core event

`event_id` is the immutable idempotency key. `vehicle_id`, `trip_id`, ISO-8601 `timestamp`, position, speed, battery state, network measurements, connection state and optional proximity/HMI fields share one event envelope for the V1 simulator.

## Analytical models

`vehicle_trip_summary`, `connectivity_summary`, `hmi_warning_performance`, `sensor_quality`, and `offline_sync_summary` are derived from Silver. They are logical Athena/QuickSight models, not sources of truth.

