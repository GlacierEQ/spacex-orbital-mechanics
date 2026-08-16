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

    # C++ remains lineage Hohmann estimate
    assert "class LambertSolver" not in cpp
    assert "tof_seconds" not in cpp

    # Python Lambert restored
    assert (ROOT / "src/alpha/lambert.py").is_file()
    assert "repository-native" in readme.lower() or LAMBERT in readme

    evidence = target.get("evidence_checkpoint", {})
    assert evidence.get("evidence_token") == TOKEN
    assert evidence.get("verified_capability") == (
        "deterministic-local-orbital-mechanics-calculation"
    )
    assert target.get("implementation_checkpoint", {}).get("deployed") is False
    assert target.get("target_architecture", {}).get("status") == (
        "PRESERVED_UNVERIFIED_TARGET_ARCHITECTURE"
    )
    assert len(target.get("target_architecture", {}).get("objectives", [])) >= 8

    assert planes.get("projection", {}).get("projection_may_overwrite_canonical_or_target") is False
    impl = planes.get("implemented", {}).get("items", [])
    impl_names = {item.get("capability") for item in impl}
    assert "real Lambert boundary-value solver" in impl_names

    assert excellence.get("product_state") == "FUNCTIONAL_LOCAL_ORBITAL_MATH_ENGINE"
    assert excellence.get("projection_state") == TOKEN
    assert "HYPER_VALIDATED" not in json.dumps(excellence, sort_keys=True)

    print(TOKEN)
    print(LAMBERT)


if __name__ == "__main__":
    main()
