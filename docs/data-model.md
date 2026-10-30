# Data model

## Core event

`event_id` is the immutable idempotency key. `vehicle_id`, `trip_id`, ISO-8601 `timestamp`, position, speed, battery state, network measurements, connection state and optional proximity/HMI fields share one event envelope for the V1 simulator.

## Analytical models

`vehicle_trip_summary`, `connectivity_summary`, `hmi_warning_performance`, `sensor_quality`, and `offline_sync_summary` are derived from Silver. They are logical Athena/QuickSight models, not sources of truth. The initial deployed catalogue table is `drivesense_dev_catalog.telemetry_silver`, scoped to the recorded controlled run; broader run aggregation needs an explicit data-layout evolution.

## Geographic scenarios

The public synthetic sample distinguishes `SAO_PAULO_URBAN`, `SAO_PAULO_FLORIANOPOLIS_CORRIDOR`, `FLORIANOPOLIS_TRAILS` and `SP_FLORIANOPOLIS_CONNECTIVITY_VARIATION`. Each event can carry `scenario`, `route_id`, `route_segment`, `region_type`, `offline_duration_s`, `reconnection_count` and `sync_duration_ms`. These are simulated route envelopes for analysis; they are not real vehicle tracks or coverage measurements.

## Multimedia and operational context

The extended synthetic envelope adds connectivity (`packet_loss_pct`, `network_provider`, `bytes_buffered`), navigation (`road_class`, `distance_remaining_km`, `eta_minutes`, `reroute_count`, `map_match_confidence`), HMI (`screen_id`, `interaction_type`, `warning_level`, `driver_action`, `driver_response_time_ms`), vehicle health (`battery_temperature_c`, `energy_consumption_kwh`, `range_estimate_km`, `tire_pressure_status`, `vehicle_state`), DataOps (`ingested_at`, `late_arrival_seconds`, `retry_count`, `processing_latency_ms`) and synthetic context (`weather_condition`, `road_surface`, `traffic_level`, `visibility_level`). No personal content, user identity, precise home/work location or real coverage data is collected.

