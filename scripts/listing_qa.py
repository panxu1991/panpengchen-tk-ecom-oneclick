#!/usr/bin/env python3
"""Listing QA checklist for a Vietnam cross-border general-merchandise listing.

Input is JSON with a "checks" object where keys are check names and values are
true/false, plus a "required" list of check names. Output is pass/fail with a
repair list. This is deterministic validation, not a compliance verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

REQUIRED_BY_DEFAULT = [
    "category",
    "attributes",
    "tax_sensitive_price",
    "title_claims",
    "images",
    "variants",
    "inventory",
    "price",
    "shipping",
    "returns",
    "documents",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", help="JSON file path, or - for stdin")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return 2

    try:
        if args.input == "-":
            raw = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not isinstance(raw, dict):
        print("error: input must be a JSON object", file=sys.stderr)
        return 1

    checks = raw.get("checks", {})
    required = raw.get("required", REQUIRED_BY_DEFAULT)

    failed: list[str] = []
    for name in required:
        if name not in checks:
            failed.append(f"{name} (missing)")
        elif bool(checks[name]) is not True:
            failed.append(name)

    result: dict[str, Any] = {
        "sku": raw.get("sku", "unnamed"),
        "pass": not failed,
        "failed_checks": failed,
        "checked_count": len(checks),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
