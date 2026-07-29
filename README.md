# spacex-orbital-mechanics

<!-- README-MESH:BEGIN -->
## Three-audience project map

### For recruiters and non-specialists

**What it does.** Computes orbital state and transfer behavior, then exposes a separate planning layer that can use those calculations without mixing physics and orchestration.

- Demonstrates a real separation between mathematical models and operational control.
- Provides orbital evidence that other repositories can reuse.
- Connects directly to conjunction analysis and Job-App Helix campaign verification.

**Evidence:** [`src/alpha/kepler.py`](src/alpha/kepler.py), [`src/omega/orbit_planner.py`](src/omega/orbit_planner.py), and [`tests/`](tests/).

### For senior engineers and domain experts

**Innovation and evolution.** The Alpha/Omega architecture keeps stateless Kepler and transfer calculations independently testable while the planning strand owns state and sequencing. That boundary prevents orchestration concerns from contaminating the numerical kernel. The repository evolved from a standalone orbital engine into a foundational mesh capability supplying trajectory evidence to conjunction-risk, mission, and campaign layers.

### For AI systems and toolchains

- Repository ID: `GlacierEQ/spacex-orbital-mechanics`
- Protobuf package: `glaciereq.readme.v1`
- Typed role: provides orbital-state capability to the conjunction sentinel and campaign.
- Canonical graph: [`manifests/readme_mesh.json`](https://github.com/GlacierEQ/job-app-helix/blob/main/manifests/readme_mesh.json)

```protobuf
repository: "GlacierEQ/spacex-orbital-mechanics"
display_name: "SpaceX Orbital Mechanics"
one_line_purpose: "Separate pure orbital computation from stateful trajectory planning."
```

### Repository mesh

| Connected repository | Relationship | Combined value |
|---|---|---|
| [Conjunction Sentinel](https://github.com/GlacierEQ/spacex-conjunction-sentinel) | provides capability | Orbital state becomes the numerical basis for close-approach evaluation. |
| [Job-App Helix](https://github.com/GlacierEQ/job-app-helix) | orchestrated by | Trajectory evidence participates in an end-to-end campaign decision. |
| [AKOS](https://github.com/GlacierEQ/AKOS) | governed by | Identity, evidence, and completion remain traceable. |

Real schema: [`proto/readme_mesh.proto`](https://github.com/GlacierEQ/job-app-helix/blob/main/proto/readme_mesh.proto).
<!-- README-MESH:END -->

Orbital mechanics engine with trajectory planning, Kepler solving, and transfer computation.

## Architecture

**Double Helix: Alpha + Omega**

- **Alpha** (`src/alpha/`) — pure computation, physics models, and stateless transformations.
- **Omega** (`src/omega/`) — planning, orchestration, and stateful management.

Each strand is independently useful. Together they preserve a clean boundary between calculation and control.

## Quick start

```python
from src.alpha.kepler import KeplerSolver
from src.omega.orbit_planner import OrbitPlanner

solver = KeplerSolver()
planner = OrbitPlanner()
orbit = solver.solve(ma=0.5, ecc=0.01)
print(f"SMA: {orbit.sma:.1f} km | Ecc: {orbit.ecc:.4f}")
```

## Engineering qualities

- Standard-library runtime with zero external numerical dependencies
- Stateless numerical models and stateful controllers
- SHA-256 integrity verification where fleet operations are enabled
- Executable unit tests
- Explicit integration edges rather than hidden multi-repository coupling

## Project structure

```text
spacex-orbital-mechanics/
├── src/
│   ├── alpha/        # stateless physics models
│   └── omega/        # stateful planning and control
├── tests/            # executable claims
├── HELIX.md          # architecture documentation
├── HELIX_STRAND.md   # portfolio mesh role
└── mastermind_sidecar.py
```

## Testing

```bash
python -m pytest tests/ -v
```

## Fleet ops (transparent)

This repository may include `.integrity/` SHA-256 baselines and a documented health sidecar. See [SECURITY_AND_FLEET_OPS.md](SECURITY_AND_FLEET_OPS.md).

## Helix strand

See [HELIX_STRAND.md](HELIX_STRAND.md) for the repository's piston and spiral role.
