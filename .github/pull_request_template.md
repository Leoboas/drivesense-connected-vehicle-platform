## Summary

Describe the change and the user or operational outcome.

## Validation

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy src`
- [ ] `pytest`
- [ ] `terraform fmt -check -recursive` and `terraform validate` (when Terraform changes)

## Cloud safety

- [ ] No AWS resources were changed by this pull request.
- [ ] If an apply, query, or Glue run is proposed, the reviewed plan/evidence and explicit approval are linked here.

## Documentation

- [ ] Architecture, runbook, ADR, or README changes are included when relevant.
