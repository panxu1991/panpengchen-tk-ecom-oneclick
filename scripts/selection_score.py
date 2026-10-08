#!/usr/bin/env python3
"""Score general-merchandise candidate SKUs for the Vietnam cross-border store.

Each dimension is 0-5. Weights produce a 0-100 score. Input is JSON (a list of
candidates). Scores are judgment inputs, not compliance approval.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

WEIGHTS = {
    "demand": 20,
    "margin": 20,
    "contentability": 15,
    "logistics_fit": 15,
    "return_risk_inverse": 15,
    "compliance_ip": 10,
    "replenishment": 5,
}

DIMENSIONS = tuple(WEIGHTS.keys())


def score_one(raw: dict[str, Any]) -> dict[str, Any]:
    name = raw.get("name", "unnamed")
    dims: dict[str, int] = {}
    for dim in DIMENSIONS:
        try:
            value = int(raw.get(dim, 0))
        except (TypeError, ValueError):
            raise ValueError(f"{name}.{dim} must be an integer 0-5")
        if value < 0 or value > 5:
            raise ValueError(f"{name}.{dim} must be between 0 and 5")
        dims[dim] = value

    weighted = sum(dims[dim] * WEIGHTS[dim] for dim in DIMENSIONS)
    score = weighted / 5  # max 100

    if score >= 80:
        decision = "advance"
    elif score >= 65:
        decision = "test"
    elif score >= 50:
        decision = "watch"
    else:
        decision = "reject"

    return {
        "name": name,
        "dimensions": dims,
        "score": round(score, 1),
        "decision": decision,
        "notes": raw.get("notes", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", help="JSON file path (list), or - for stdin")
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
        if not isinstance(raw, list):
            raise ValueError("input must be a JSON list")
        results = [score_one(item) for item in raw]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results.sort(key=lambda r: r["score"], reverse=True)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
