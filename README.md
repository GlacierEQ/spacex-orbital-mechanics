# spacex-orbital-mechanics

Orbital mechanics engine with trajectory optimization and Hohmann transfer computation

## Architecture

**Double Helix (Alpha + Omega)**

- **Alpha** (`src/alpha/`): Pure computation — physics models, stateless transformations
- **Omega** (`src/omega/`): Control layer — orchestration, stateful management

## Quick Start

```python
from src.alpha.kepler import KeplerSolver\nfrom src.omega.orbit_planner import OrbitPlanner\nsolver = KeplerSolver()\nplanner = OrbitPlanner()\norbit = solver.solve(ma=0.5, ecc=0.01)\nprint(f'SMA: {orbit.sma:.1f} km | Ecc: {orbit.ecc:.4f}')
```

## Key Features

- Zero external dependencies (stdlib only)
- Stateless alpha models, stateful omega controllers
- SHA-256 file integrity verification
- Shadow watchdog daemon monitoring
- Mastermind sidecar for cross-domain coordination

## Project Structure

```
spacex-orbital-mechanics/
├── src/
│   ├── alpha/        # Physics models (stateless)
│   └── omega/        # Controllers (stateful)
├── tests/            # Unit tests
├── HELIX.md          # Architecture documentation
├── AGENTS.md         # Agent configuration
└── mastermind_sidecar.py  # Cross-domain health
```

## Testing

```bash
python -m pytest tests/ -v
```

---

## Fleet ops (transparent)

This repo may include `.integrity/` (SHA-256 integrity) and/or a health sidecar.
These are **documented fleet operations**, not covert implants. See [SECURITY_AND_FLEET_OPS.md](SECURITY_AND_FLEET_OPS.md).

## Helix strand

See [HELIX_STRAND.md](HELIX_STRAND.md) — piston/spiral role in the portfolio double helix.
