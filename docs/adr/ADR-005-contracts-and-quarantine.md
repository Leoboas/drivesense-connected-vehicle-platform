# ADR-005: Versioned contracts and quarantine

**Problem:** malformed or silently evolved events could corrupt Silver/Gold models. **Decision:** validate raw payloads against a versioned compatibility policy and append rejected payloads to an immutable JSONL quarantine record. **Alternative:** drop invalid events or make every new field a breaking change. **Trade-off:** quarantine requires a later reprocessing workflow, but preserves evidence and prevents silent loss.

