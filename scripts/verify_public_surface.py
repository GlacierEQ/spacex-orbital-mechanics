from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"
LAMBERT = "REPOSITORY_NATIVE_LAMBERT_TWO_BODY"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    readme = read("README.md")
    cpp = read("src/lambert_solver.cpp")
    julia = read("src/orbital_integrator.jl")
    lambert = read("src/alpha/lambert.py")
    capabilities = json.loads(read("machine/capabilities.json"))
    target = json.loads(read("machine/target-contract.json"))
    planes = json.loads(read("machine/capability-planes.json"))
    excellence = json.loads(read("machine/excellence-state.json"))

    assert TOKEN in readme
    assert TOKEN in cpp
    assert TOKEN in julia
    assert TOKEN in lambert
    assert LAMBERT in lambert
    assert capabilities.get("evidence_token") == TOKEN
    assert "not affiliated with, endorsed by, or connected to SpaceX" in readme
    assert "Fully connected to APEX Highway mesh" not in readme
    assert "trajectory calculation endpoint for flight agents" not in readme
    assert "hyper-scaling" not in capabilities.get("capabilities", [])

    assert "class LambertSolver" not in cpp
    assert "tof_seconds" not in cpp
    assert (ROOT / "src/alpha/lambert.py").is_file()

    evidence = target["evidence_checkpoint"]
    assert evidence["evidence_token"] == TOKEN
    assert evidence["verified_capability"] == "deterministic-local-orbital-mechanics-calculation"
    assert evidence["verified_checkpoint_head"] == "b99a1f7ea0534d3a268f9bea432399c9862bd1e4"
    assert evidence["restored_capability_token"] == LAMBERT
    assert target["implementation_checkpoint"]["deployed"] is False
    assert target["target_architecture"]["status"] == "ACTIVE_FRONTIER"
    assert target["apex"]["selection_mode"] == "CURRENT_BEST_REVISABLE"
    assert len(target["target_architecture"]["objectives"]) >= 8

    assert planes["schema"] == "glaciereq.repository-capability-evolution.v2"
    assert planes["apex"]["selection_mode"] == "CURRENT_BEST_REVISABLE"
    assert planes["apex"]["capability_donor_preservation"] is True
    assert planes["selection"]["challengeable"] is True
    selected = {item["capability"] for item in planes["selection"]["capabilities"]}
    assert "repository-native-lambert-two-body" in selected
    assert len(planes["capability_donors"]) >= 3
    assert planes["projection"]["projection_may_overwrite_intent_or_target"] is False
    assert planes["target"]["status"] == "ACTIVE_FRONTIER"

    targets = {item["capability"] for item in planes["target"]["items"]}
    assert "fully verified Lambert boundary-value solver" in targets
    assert "higher-order or adaptive two-body propagation" in targets
    assert "N-body and perturbation-aware orbital propagation" in targets

    assert excellence["schema"] == "glaciereq.repo-excellence-state.v3"
    assert excellence["product_state"] == "FUNCTIONAL_LOCAL_ORBITAL_MATH_ENGINE"
    assert excellence["target_state"] == "ACTIVE_FRONTIER"
    assert excellence["selection_state"] == "CURRENT_BEST_REVISABLE"
    assert excellence["selection_challengeable"] is True
    assert excellence["capability_donor_preservation"] is True
    assert excellence["evidence_checkpoint"]["restored_research_capability"] == LAMBERT
    assert "HYPER_VALIDATED" not in json.dumps(excellence, sort_keys=True)

    print(TOKEN)
    print(LAMBERT)


if __name__ == "__main__":
    main()
