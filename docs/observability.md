# Observability and portfolio SLOs

The local processor emits one JSON log per data-quality decision, with timestamp, component, status, correlation ID, event ID and schema version; successful records also carry vehicle/trip IDs. It reports `events_received`, `events_processed`, `events_invalid`, `events_quarantined`, `duplicates_detected`, `late_events`, and `offline_events`. These field names are intentionally suitable for later CloudWatch metric filters, but no always-on dashboard is provisioned.

Portfolio targets, not production commitments: data-quality score >98%, reconciliation success >99%, and successful on-demand pipeline execution >99%. Their evidence must come from a real recorded run, not an assertion in documentation.

