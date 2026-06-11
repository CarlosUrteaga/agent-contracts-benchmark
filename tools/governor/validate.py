"""Validate one manifest against one contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import validate_manifest_against_contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args()

    result = validate_manifest_against_contract(Path(args.manifest), Path(args.contract))
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
