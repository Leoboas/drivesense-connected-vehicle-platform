# Contributing to DriveSense

## Development

Use Python 3.11 or newer. Create a virtual environment, then install the development and UI
extras when changing the dashboard:

```powershell
pip install -e ".[dev,ui]"
ruff check .
ruff format --check .
mypy src
pytest
```

## Pull requests

Keep changes focused, include tests for changed behaviour, and explain any data-contract or
infrastructure consequence. Open feature pull requests into `develop`; promote reviewed
`develop` releases into `main`. Do not commit credentials, Terraform state, generated cloud
datasets, or saved Terraform plans.

## Infrastructure safety

Terraform plans and applies must target `us-east-2`. A plan is review evidence, not permission
to apply. Never run an apply, Glue job, Athena query, crawler, benchmark, or deletion without the
required review and explicit authorization.
