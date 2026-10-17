from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def preflight(region: str, profile: str | None = None) -> dict[str, Any]:
    """Read-only identity check; credentials use the standard AWS provider chain."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError as error:
        raise RuntimeError("Install the cloud extra: pip install -e '.[cloud]'") from error
    session = boto3.Session(profile_name=profile, region_name=region)
    config = Config(
        retries={"total_max_attempts": 2, "mode": "adaptive"}, connect_timeout=5, read_timeout=10
    )
    identity = session.client("sts", config=config).get_caller_identity()
    return {"account_id": identity["Account"], "principal_arn": identity["Arn"], "region": region}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Perform a read-only DriveSense AWS identity preflight."
    )
    parser.add_argument("--region", required=True)
    parser.add_argument("--profile")
    args = parser.parse_args()
    try:
        print(json.dumps(preflight(args.region, args.profile), indent=2))
        return 0
    except Exception as error:
        print(f"AWS preflight failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
