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
    planes = json.loads(read("machine/capability-planes.json"))
    excellence = json.loads(read("machine/excellence-state.json"))

    assert TOKEN in readme
    assert TOKEN in cpp
    assert TOKEN in julia
    assert capabilities["evidence_token"] == TOKEN
    assert "not affiliated with, endorsed by, or connected to SpaceX" in readme
    assert "production Lambert solver" in readme
    assert "Fully connected to APEX Highway mesh" not in readme
    assert "trajectory calculation endpoint for flight agents" not in readme
    assert "high-precision numerical stability" not in readme.lower()
    assert "class LambertSolver" not in cpp
    assert "tof_seconds" not in cpp
    assert "hyper-scaling" not in capabilities["capabilities"]

    evidence = target["evidence_checkpoint"]
    assert evidence["evidence_token"] == TOKEN
    assert evidence["verified_capability"] == (
        "deterministic-local-orbital-mechanics-calculation"
    )
    assert evidence["canonical_proof_head"] == (
        "b99a1f7ea0534d3a268f9bea432399c9862bd1e4"
    )
    assert target["implementation_checkpoint"]["deployed"] is False
    assert target["target_architecture"]["status"] == (
        "PRESERVED_UNVERIFIED_TARGET_ARCHITECTURE"
    )
    assert len(target["target_architecture"]["objectives"]) >= 8

    assert planes["projection"]["projection_may_overwrite_canonical_or_target"] is False
    assert planes["target"]["status"] == "PRESERVED_UNVERIFIED_TARGET_ARCHITECTURE"
    assert len(planes["target"]["items"]) >= 8
    target_states = {item["state"] for item in planes["target"]["items"]}
    assert "UNVERIFIED_TARGET" in target_states
    assert "PARTIALLY_IMPLEMENTED_TARGET" in target_states

    target_names = {item["capability"] for item in planes["target"]["items"]}
    assert "real Lambert boundary-value solver" in target_names
    assert "N-body and perturbation-aware orbital propagation" in target_names
    assert "programmatic orbital-calculation service" in target_names
    assert "governed orbital-event or agent integration" in target_names

    assert excellence["product_state"] == "FUNCTIONAL_LOCAL_ORBITAL_MATH_ENGINE"
    assert excellence["evidence_state"] == "EXACT_HEAD_VERIFIED"
    assert excellence["projection_state"] == TOKEN
    assert excellence["target_state"] == "PRESERVED_UNVERIFIED_TARGET_ARCHITECTURE"
    assert excellence["evidence_checkpoint"]["head_sha"] == (
        "b99a1f7ea0534d3a268f9bea432399c9862bd1e4"
    )
    assert "HYPER_VALIDATED" not in json.dumps(excellence, sort_keys=True)

    print(TOKEN)


if __name__ == "__main__":
    main()
