# Data quality

Rules flag missing identifiers/timestamps, malformed timestamps, negative speed, battery state outside 0–100, implausible signal strength, HMI display timestamps before generation, and duplicate event IDs. Invalid or duplicate events are excluded from valid analytical aggregates; raw Bronze remains unchanged for investigation.

`data_quality_score = 100 × valid records / evaluated records`. It is intentionally a basic operational metric, not a statistical guarantee. Suspicious signals remain available but are flagged rather than discarded.

