#!/usr/bin/env python3
"""Execute selected local orbital capabilities and emit a deterministic receipt."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alpha.kepler import MU_EARTH, orbital_period, solve_kepler  # noqa: E402
from alpha.lambert import EVIDENCE_STATE, SOLVER_IDENTITY, solve_lambert  # noqa: E402


def _stable(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_receipt() -> dict:
    eccentric_anomaly = solve_kepler(1.0, 0.1)
    period_seconds = orbital_period(7_000_000.0, MU_EARTH)
    solution = solve_lambert(
        (6_771_000.0, 0.0, 0.0),
        (-42_164_000.0, 0.0, 0.0),
        5.0 * 3600.0,
        mu=MU_EARTH,
        short_way=True,
    )
    body = {
        "schema": "glaciereq.orbital-operate-receipt.v1",
        "selection_mode": "CURRENT_BEST_REVISABLE",
        "capabilities": [
            "kepler-equation-solving",
            "repository-native-lambert-two-body",
        ],
        "evidence_state": EVIDENCE_STATE,
        "lambert_method": solution.method,
        "lambert_residual_seconds": solution.residual,
        "lambert_departure_speed_mps": math.sqrt(sum(value * value for value in solution.v1)),
        "eccentric_anomaly_rad": eccentric_anomaly,
        "period_seconds": period_seconds,
        "external_actions_executed": 0,
    }
    return {**body, "receipt_sha256": hashlib.sha256(_stable(body)).hexdigest()}


def main() -> int:
    receipt = build_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    valid = (
        receipt["evidence_state"] == EVIDENCE_STATE
        and receipt["selection_mode"] == "CURRENT_BEST_REVISABLE"
        and receipt["lambert_method"] == SOLVER_IDENTITY
        and math.isfinite(receipt["lambert_departure_speed_mps"])
        and receipt["lambert_residual_seconds"] < 1.0
        and math.isfinite(receipt["eccentric_anomaly_rad"])
        and receipt["period_seconds"] > 0.0
        and receipt["external_actions_executed"] == 0
        and len(receipt["receipt_sha256"]) == 64
    )
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
