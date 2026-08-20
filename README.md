# Orbital Mechanics Laboratory

> **Deterministic local orbital-mechanics calculations for Kepler equations, state-vector conversion, classical transfer estimates, bounded perturbation experiments, and a restored repository-native Lambert research solver.**

This is an independent GlacierEQ portfolio repository. It is **not affiliated with, endorsed by, or connected to SpaceX** and has no access to proprietary SpaceX, Falcon, Starship, mission-planning, navigation, guidance, or flight-control systems.

It is not an N-body or high-precision production flight integrator.

Evidence state: `LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY`

## Verified repository-owned scope

The public evidence surface includes:

- elliptic and hyperbolic Kepler-equation solving;
- Stumpff helper functions;
- classical orbital-element ↔ state-vector conversion for bounded non-degenerate fixtures;
- vis-viva and orbital-period calculations;
- Hohmann and bi-elliptic transfer estimates;
- plane-change calculations;
- bounded J2 secular-rate experiments;
- local Python tests and cold-start operability;
- a small C++ **transfer-speed estimate** reference program.

### APEX capability recovery

| Plane | Capability | Evidence |
|---|---|---|
| **VERIFIED CHECKPOINT** | classical Kepler / Hohmann / J2 laboratory math | `LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY` |
| **SELECTED RESEARCH CAPABILITY** | repository-native two-body Lambert + Lambert-cost porkchop | `REPOSITORY_NATIVE_LAMBERT_TWO_BODY` |
| **DONOR** | C++ classical transfer-speed reference | `src/lambert_solver.cpp` |
| **DONOR / CHALLENGER** | Julia two-body propagation reference | `src/orbital_integrator.jl` |

`src/alpha/lambert.py` is a **real two-body Lambert boundary-value solver** using a universal-variable style method for research. It remains selected as a research capability while fresh expanded proof is built. It is **not** flight-dynamics authority, **not** an N-body or high-precision production flight integrator, and **not** SpaceX mission software.

`src/lambert_solver.cpp` retains its historical filename as a Hohmann transfer-speed estimate and comparison donor. Python holds the restored Lambert mechanism.

`src/orbital_integrator.jl` remains a simple two-body Euler-step reference and donor for future higher-order propagation work.

## Core implementation

| Path | Role |
|---|---|
| `src/alpha/kepler.py` | Selected Kepler equations, orbital state/element math, J2 helpers |
| `src/alpha/lambert.py` | Selected repository-native Lambert two-body research solver |
| `src/omega/orbit_planner.py` | Classical transfers + Lambert-cost porkchop samples |
| `src/lambert_solver.cpp` | C++ Hohmann speed-estimate donor/comparison surface |
| `src/orbital_integrator.jl` | Julia two-body Euler-step donor/challenger |
| `tests/test_orbital.py` | Repository-native Python mechanics tests |
| `tests/test_lambert_solver.py` | Lambert solver tests |
| `tests/test_public_truth.py` | Public-claim and capability-plane boundary tests |
| `scripts/verify_public_surface.py` | Fail-closed public truth verifier |
| `machine/capability-planes.json` | APEX selections, challengers, donors, target frontier, evidence, and lineage |

## APEX evolution

Selection occurs per capability, not per repository or language. The restored Lambert mechanism can remain selected while C++ and Julia retain donor value, and higher-order propagation, N-body dynamics, rendezvous workflows, programmatic services, numerical benchmarks, covariance, sensor-fusion, and operator-console research remain visible frontiers.

Fresh proof can strengthen or replace a selection. Lack of current proof narrows public projection, but it does not silently delete implemented research or ambitious target state.

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

Any future claim above this ceiling requires new source, deterministic tests, exact-head receipts, and successful APEX capability-graph re-evaluation for the relevant capability.

## Reproduce the evidence surface

```bash
bash scripts/ci/verify.sh
```

The gate compiles the Python surface, runs deterministic tests, compiles/runs the C++ reference program, and verifies the public/machine truth boundary.
