# DriveSense Connected Vehicle Platform

Cloud-native, offline-first telemetry analytics platform for a fictional connected-vehicle fleet. It is designed as an engineering portfolio project: realistic failure modes, explicit data-quality controls, and cloud analytics rather than a dashboard-only demo.

> This project is an independent engineering portfolio project. It is not affiliated with, endorsed by, or developed for BMW Group, Volvo Cars, ACT Digital, or any automotive manufacturer. All vehicle data is synthetic or publicly available.

## Architecture

```text
Vehicle simulator → SQLite edge buffer → S3 Bronze (immutable JSON)
                                      → Glue crawler / PySpark → S3 Silver (Parquet)
                                      → Athena Gold views → QuickSight-ready datasets
```

The simulator deliberately produces duplicate IDs, late/out-of-order arrivals, invalid readings, missing HMI warnings, poor signal and offline periods. Recovery sends buffered events in temporal order and uses `event_id` as the idempotency key.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python scripts/generate_telemetry.py --vehicles 10 --trips 20 --events 1000 --output data/generated/telemetry.jsonl
pytest
docker build .
```

## Stack and delivery

- Python 3.11, SQLite edge buffer, pytest, Ruff and mypy
- Amazon S3 Bronze/Silver, Glue catalog/crawler/PySpark job, Athena workgroup and SQL models
- Terraform modules with encrypted-at-rest AWS defaults, public-access blocks, tags and least-privilege Glue role
- GitHub Actions validates Python, Terraform and Docker; it never deploys AWS infrastructure

See [architecture](docs/architecture.md), [offline-first design](docs/offline-first.md), [data quality](docs/data-quality.md), [cost model](docs/cost-model.md), and [interview notes](docs/interview-notes.md).

## Infrastructure

Terraform intentionally has no automatic apply. Authenticate using an external AWS profile/SSO, then review the plan:

```bash
terraform -chdir=infra/terraform/environments/dev init
terraform -chdir=infra/terraform/environments/dev plan
```

## Limitations and roadmap

V1 uses deterministic simulation and a simple route-score baseline; it does not claim real-world coverage prediction, maps, OEM data, streaming infrastructure, or automated QuickSight provisioning. See the backlog for next steps.

