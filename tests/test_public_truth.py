from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alpha.kepler import OrbitalElements, coe_to_state, solve_kepler, state_to_coe
from alpha.lambert import SOLVER_IDENTITY, solve_lambert
from omega.orbit_planner import hohmann_transfer

TOKEN = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(read(path))


def test_public_surface_is_explicitly_non_affiliated() -> None:
    readme = read("README.md")
    assert TOKEN in readme
    assert "not affiliated with, endorsed by, or connected to SpaceX" in readme
    assert "not an N-body or high-precision production flight integrator" in readme or "not an N-body" in readme
    assert "Fully connected to APEX Highway mesh" not in readme
    assert "trajectory calculation endpoint for flight agents" not in readme
    # Counter-engineering: must acknowledge restored Lambert plane
    assert "Lambert" in readme
    assert SOLVER_IDENTITY in readme or "repository-native Lambert" in readme.lower() or "repository-native lambert" in readme.lower()


def test_lambert_module_exists_and_solves() -> None:
    src = read("src/alpha/lambert.py")
    assert SOLVER_IDENTITY in src
    assert TOKEN in src
    r1 = (7_000_000.0, 0.0, 0.0)
    r2 = (0.0, 7_000_000.0, 0.0)
    sol = solve_lambert(r1, r2, 3000.0)
    assert sol.method == SOLVER_IDENTITY
    assert math.isfinite(sum(sol.v1))


def test_historical_cpp_filename_lineage() -> None:
    cpp = read("src/lambert_solver.cpp")
    assert TOKEN in cpp
    # C++ file remains Hohmann speed reference lineage; Python holds real Lambert
    assert "Hohmann" in cpp or "hohmann" in cpp


def test_julia_reference_is_labeled_first_order_and_non_production() -> None:
    julia = read("src/orbital_integrator.jl")
    assert TOKEN in julia
    assert "not an N-body, high-precision, production" in julia
    assert "euler_two_body_step" in julia


def test_machine_truth_allows_implemented_lambert_plane() -> None:
    capabilities = load("machine/capabilities.json")
    target = load("machine/target-contract.json")
    excellence = load("machine/excellence-state.json")
    assert "hyper-scaling" not in capabilities.get("capabilities", [])
    assert capabilities.get("evidence_token") == TOKEN or TOKEN in json.dumps(capabilities)
    assert target.get("evidence_token") == TOKEN or TOKEN in json.dumps(target)
    assert excellence.get("evidence_token") == TOKEN or TOKEN in json.dumps(excellence)
    assert target.get("current", {}).get("deployed") is False
    assert "HYPER_VALIDATED" not in json.dumps(excellence, sort_keys=True)
    # dual plane recovery fields if present
    caps = capabilities.get("capabilities", [])
    if isinstance(caps, list):
        assert "deterministic-local-orbital-mechanics-calculation" in caps or any(
            "orbital" in str(c) for c in caps
        )


def test_kepler_and_state_conversion_reproduce_bounded_invariants() -> None:
    mean_anomaly = 1.0
    eccentricity = 0.3
    eccentric_anomaly = solve_kepler(mean_anomaly, eccentricity)
    residual = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly)
    assert abs(residual - mean_anomaly) < 1e-10

    elements = OrbitalElements(
        a=7_000_000.0,
        e=0.01,
        i=0.5,
        raan=1.0,
        argp=0.3,
        ta=0.7,
    )
    recovered = state_to_coe(coe_to_state(elements))
    assert abs(recovered.a - elements.a) < 1.0
    assert abs(recovered.e - elements.e) < 1e-6
    assert abs(recovered.i - elements.i) < 1e-4


def test_classical_hohmann_estimate_is_finite_and_positive() -> None:
    result = hohmann_transfer(6_771_000.0, 42_164_000.0)
    assert math.isfinite(result.total_dv)
    assert result.dv1 > 0
    assert result.dv2 > 0
    assert result.tof > 0
