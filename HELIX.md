# HELIX Architecture — spacex-orbital-mechanics

## Double Helix Pattern

**Alpha (What)** — Pure physics models, stateless computation
- kepler

**Omega (How)** — Controllers, orchestration, stateful management  
- orbital_surfing,orbit_planner

## Design Principles

- Zero external dependencies (stdlib only)
- Stateless alpha, stateful omega
- SHA-256 file integrity verification
- Shadow watchdog daemon monitoring
- Mastermind sidecar coordination

## Data Flow

```
Alpha Models → Omega Controllers → Mastermind Sidecar → Shadow Infrastructure
```
