# SpaceX Orbital Mechanics — C++ & Julia Kepler Trajectory Integrator 🌌

> **C++ Lambert solver & Julia differential equation integrator for orbital mechanics and trajectory propagation.**

[![C++](https://img.shields.io/badge/C++-17-00599C)]()
[![Julia](https://img.shields.io/badge/Julia-1.9+-9558B2)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![Domain](https://img.shields.io/badge/Domain-Astrodynamics-blue)]()

---

## 🎯 For Recruiters & Hiring Managers

This repository implements **SpaceX Orbital Mechanics** — solving Lambert's problem and propagating Keplerian orbital differential equations in C++ and Julia. It demonstrates:

- **C++ Lambert solver** calculating orbital delta-V maneuver requirements between 3D vectors
- **Julia ODE integrator** solving N-body gravitational differential equations at high precision
- **Python orbital mechanics suite** computing Hohmann transfers, inclination changes, and orbital elements
- **High-precision numerical stability** preserving energy and angular momentum over long propagation timelines

**Why this matters**: Orbital mechanics requires fast, deterministic numerical solvers to compute transfer burns, rendezvous trajectories, and constellation stationkeeping in real time.

---

## 🔬 For Engineers & Technical Reviewers

### Core Components

| Component | Language | Purpose |
|---|---|---|
| `src/lambert_solver.cpp` | C++ | C++ class for Lambert delta-V trajectory calculation |
| `julia/orbital_differential.jl` | Julia | High-precision Julia ODE integrator for Kepler orbits |
| `tests/test_lambert_solver.py` | Python | Test wrapper verifying delta-V calculations |

---

## 🤖 ML/AI & Programmatic Mesh Integration

- **MCP Tool**: `compute_orbital_transfer()` — trajectory calculation endpoint for flight agents
- **Mastermind Sidecar**: Fully connected to APEX Highway mesh
- **SHA-256 Integrity**: Tracked in `.integrity/file_hashes.json`

---

## ⚡ Quick Start

```bash
python3 tests/test_lambert_solver.py
```
