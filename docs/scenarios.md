# Reproducible portfolio scenario

Run `python scripts/run_demo.py --events 100`. The deterministic scenario creates offline telemetry, deliberately retries a failed synchronization, recovers through the SQLite buffer, deduplicates logical events, and computes HMI warning metrics. It writes `data/local/demo/report.json`; generated local evidence is excluded from Git.

The report distinguishes attempted duplicates from persisted logical records. Missing warning means a sensor condition was detected but no display occurred. False warning means a display occurred without a detected object. Latency is measured from telemetry timestamp to generation, generation to display, and end to end; threshold breaches are explicit.
