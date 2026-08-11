# Orbital Mechanics Laboratory

> **Deterministic local orbital-mechanics calculations for Kepler equations, state-vector conversion, classical transfer estimates, and bounded perturbation experiments.**

This is an independent GlacierEQ portfolio repository. It is **not affiliated with, endorsed by, or connected to SpaceX** and has no access to proprietary SpaceX, Falcon, Starship, mission-planning, navigation, guidance, or flight-control systems.

Evidence state: `LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY`

## Verified repository-owned scope

The public admission surface is the code and tests that this repository can reproduce locally:

- elliptic and hyperbolic Kepler-equation solving;
- Stumpff helper functions;
- classical orbital-element ↔ state-vector conversion for bounded non-degenerate fixtures;
- vis-viva and orbital-period calculations;
- Hohmann and bi-elliptic transfer estimates;
- plane-change calculations;
- bounded J2 secular-rate experiments;
- local Python tests and cold-start operability;
- a small C++ **transfer-speed estimate** reference program.

`src/lambert_solver.cpp` retains its historical filename, but the current program is **not a Lambert boundary-value solver**. A true Lambert solver must use both position vectors and time-of-flight to solve the transfer orbit; the historical implementation did not. The public surface does not claim Lambert capability until that mechanism exists and is independently tested.

`src/orbital_integrator.jl` is a simple two-body Euler-step reference sketch. It is not an N-body or high-precision integrator and is not part of the admitted proof surface.

## Core implementation

| Path | Verified role |
|---|---|
| `src/alpha/kepler.py` | Kepler equations, orbital state/element math, bounded perturbation helpers |
| `src/omega/orbit_planner.py` | Classical transfer and plane-change estimates |
| `src/lambert_solver.cpp` | Historical-filename C++ transfer-speed estimate, explicitly not Lambert |
| `src/orbital_integrator.jl` | Two-body Euler-step reference sketch, not high precision |
| `tests/test_orbital.py` | Repository-native Python mechanics tests |
| `tests/test_public_truth.py` | Public-claim and machine-state boundary tests |
| `scripts/verify_public_surface.py` | Fail-closed public truth verifier |

## Evidence boundary

This repository does **not** claim:

- SpaceX affiliation, endorsement, employment, or proprietary access;
- a production Lambert solver;
- N-body or high-precision long-duration integration;
- proven long-horizon energy/angular-momentum conservation;
- real-time rendezvous, stationkeeping, navigation, guidance, or flight-control authority;
- real mission ephemerides or proprietary telemetry;
- live MCP, provider, agent-mesh, or APEX runtime integration;
- production performance, safety certification, deployment, or flight readiness.

Any future claim above this ceiling requires new source, deterministic tests, exact-head receipts, and a new governance admission.

## Reproduce the admitted surface

```bash
bash scripts/ci/verify.sh
```

The gate compiles the Python surface, runs deterministic tests, compiles/runs the C++ reference program, and verifies the public/machine truth boundary.
