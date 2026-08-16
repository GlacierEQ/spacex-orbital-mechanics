# Orbital Mechanics Laboratory

> **Deterministic local orbital-mechanics calculations for Kepler equations, state-vector conversion, classical transfer estimates, and bounded perturbation experiments.**

This is an independent GlacierEQ portfolio repository. It is **not affiliated with, endorsed by, or connected to SpaceX** and has no access to proprietary SpaceX, Falcon, Starship, mission-planning, navigation, guidance, or flight-control systems.

It is not an N-body or high-precision production flight integrator.

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

### Dual-plane recovery (counter-engineering)

| Plane | Capability | Evidence |
|---|---|---|
| **VERIFIED** | classical Kepler / Hohmann / J2 laboratory math | `LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY` |
| **IMPLEMENTED** | repository-native two-body Lambert + Lambert-cost porkchop | `REPOSITORY_NATIVE_LAMBERT_TWO_BODY` |

`src/alpha/lambert.py` is a **real two-body Lambert boundary-value solver** (universal-variable style) for research. It is **not** flight-dynamics authority, **not** an N-body or high-precision production flight integrator, and **not** SpaceX mission software.

`src/lambert_solver.cpp` retains historical filename as a Hohmann transfer-speed estimate (lineage). Python holds the Lambert mechanism.

`src/orbital_integrator.jl` remains a simple two-body Euler-step reference sketch.

## Core implementation

| Path | Role |
|---|---|
| `src/alpha/kepler.py` | Kepler equations, orbital state/element math, J2 helpers |
| `src/alpha/lambert.py` | Repository-native Lambert two-body solver (**implemented**) |
| `src/omega/orbit_planner.py` | Classical transfers + Lambert-cost porkchop samples |
| `src/lambert_solver.cpp` | Historical-filename C++ Hohmann speed estimate |
| `src/orbital_integrator.jl` | Two-body Euler-step reference sketch |
| `tests/test_orbital.py` | Repository-native Python mechanics tests |
| `tests/test_lambert_solver.py` | Lambert solver tests |
| `tests/test_public_truth.py` | Public-claim and dual-plane boundary tests |
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
