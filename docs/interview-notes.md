# Interview notes

## ADR-001 — SQLite edge buffer

**Problem:** cellular connectivity is unreliable. **Decision:** durable local SQLite with an event-id primary key. **Why:** transactional, inspectable and sufficient for a single simulated edge device. **Alternative:** Kafka/RabbitMQ. **Trade-off:** no distributed buffering, deliberately avoiding unnecessary operational cost. **Interview framing:** I chose the smallest durable mechanism that proves recovery and idempotency.

## ADR-002 — Bronze JSON and Silver Parquet

**Problem:** retain evidence while supporting economical analytics. **Decision:** immutable JSON Bronze, validated/deduplicated Parquet Silver. **Alternative:** transform on ingest. **Trade-off:** extra storage and ETL, but replayability and schema investigation. **Interview framing:** raw data preserves the ability to correct evolving quality logic.

