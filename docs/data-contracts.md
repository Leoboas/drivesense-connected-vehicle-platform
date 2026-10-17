# Data contracts and schema evolution

Raw producers must provide a `schema_version`. `telemetry.v1` defines the stable core envelope; `telemetry.v2` adds nullable `battery_temperature_c`, `sensor_firmware_version`, `network_provider`, and `gps_accuracy_m`. The consumer accepts both versions and ignores unknown optional fields, so a producer can make additive changes without blocking an older consumer.

Breaking changes require a new major contract version; changing the type, meaning, or requiredness of an existing field is breaking. Contract rejection happens before model construction. Rejected input is written to quarantine with the original payload, rule ID, reason, and UTC ingestion time so it can be inspected and reprocessed after remediation.

The JSON Schema documents in `schemas/` are the human/tooling contract. The small stdlib validator is deliberately used in the local V2 path to avoid making the demo depend on a schema registry; its behavior is covered by unit tests.
