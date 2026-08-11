from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    readme = read("README.md")
    cpp = read("src/lambert_solver.cpp")
    julia = read("src/orbital_integrator.jl")
    capabilities = json.loads(read("machine/capabilities.json"))
    target = json.loads(read("machine/target-contract.json"))
    excellence = json.loads(read("machine/excellence-state.json"))

    assert TOKEN in readme
    assert TOKEN in cpp
    assert TOKEN in julia
    assert capabilities["evidence_token"] == TOKEN
    assert target["evidence_token"] == TOKEN
    assert excellence["evidence_token"] == TOKEN
    assert "not affiliated with, endorsed by, or connected to SpaceX" in readme
    assert "production Lambert solver" in readme
    assert "Fully connected to APEX Highway mesh" not in readme
    assert "trajectory calculation endpoint for flight agents" not in readme
    assert "high-precision numerical stability" not in readme.lower()
    assert "class LambertSolver" not in cpp
    assert "tof_seconds" not in cpp
    assert "hyper-scaling" not in capabilities["capabilities"]
    assert target["current"]["deployed"] is False
    assert target["verified_capability"] == (
        "deterministic-local-orbital-mechanics-calculation"
    )
    assert excellence["principal_state"] == "TESTED"
    assert "HYPER_VALIDATED" not in json.dumps(excellence, sort_keys=True)

    print(TOKEN)


if __name__ == "__main__":
    main()
