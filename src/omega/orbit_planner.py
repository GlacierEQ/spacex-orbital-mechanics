from __future__ import annotations
"""Orbit-transfer laboratory: classical burns + repository-native Lambert.

Verified classical plane: Hohmann, bi-elliptic, plane-change arithmetic.
Implemented plane: two-body Lambert solver and Lambert-cost porkchop samples.
Not flight-dynamics authority; not affiliated with SpaceX.
"""

import math
from dataclasses import dataclass

from alpha.kepler import MU_EARTH
from alpha.lambert import lambert_transfer_cost, SOLVER_IDENTITY

EVIDENCE_STATE = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"


@dataclass
class TransferResult:
    dv1: float
    dv2: float
    total_dv: float
    tof: float
    transfer_a: float
    method: str
    notes: str = ""


def _positive_radius(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive radius")


def hohmann_transfer(r1: float, r2: float, mu: float = MU_EARTH) -> TransferResult:
    """Classical two-impulse Hohmann estimate between circular orbits."""
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    a_t = (r1 + r2) / 2

    v1_circ = math.sqrt(mu / r1)
    v2_circ = math.sqrt(mu / r2)
    v1_trans = math.sqrt(mu * (2 / r1 - 1 / a_t))
    v2_trans = math.sqrt(mu * (2 / r2 - 1 / a_t))

    dv1 = abs(v1_trans - v1_circ)
    dv2 = abs(v2_circ - v2_trans)
    tof = math.pi * math.sqrt(a_t ** 3 / mu)

    return TransferResult(
        dv1=dv1,
        dv2=dv2,
        total_dv=dv1 + dv2,
        tof=tof,
        transfer_a=a_t,
        method="HOHMANN",
    )


def bi_elliptic_transfer(
    r1: float, r2: float, r3: float, mu: float = MU_EARTH
) -> TransferResult:
    """Classical bi-elliptic transfer estimate via intermediate radius r3."""
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(r3, "r3")
    _positive_radius(mu, "mu")
    a1 = (r1 + r3) / 2
    a2 = (r3 + r2) / 2

    v1_circ = math.sqrt(mu / r1)
    v2_circ = math.sqrt(mu / r2)
    v1_t1 = math.sqrt(mu * (2 / r1 - 1 / a1))
    v2_t1 = math.sqrt(mu * (2 / r3 - 1 / a1))
    v1_t2 = math.sqrt(mu * (2 / r3 - 1 / a2))
    v2_t2 = math.sqrt(mu * (2 / r2 - 1 / a2))

    dv1 = abs(v1_t1 - v1_circ)
    dv2 = abs(v2_t2 - v2_circ)
    dv_mid = abs(v1_t2 - v2_t1)

    tof1 = math.pi * math.sqrt(a1 ** 3 / mu)
    tof2 = math.pi * math.sqrt(a2 ** 3 / mu)

    return TransferResult(
        dv1=dv1,
        dv2=dv2,
        total_dv=dv1 + dv_mid + dv2,
        tof=tof1 + tof2,
        transfer_a=a1,
        method="BI-ELLIPTIC",
        notes=f"mid-burn dv={dv_mid:.1f} m/s via r3={r3:.0f} m",
    )


def plane_change(v: float, delta_i: float, fpa: float = 0.0) -> float:
    """Idealized impulsive plane-change estimate."""
    if not math.isfinite(v) or v < 0:
        raise ValueError("v must be finite and non-negative")
    return 2 * v * math.sin(delta_i / 2) * math.cos(fpa)


def combined_plane_change(
    r1: float, r2: float, delta_i: float, mu: float = MU_EARTH
) -> TransferResult:
    """Hohmann estimate plus an idealized plane change at apoapsis."""
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    a_t = (r1 + r2) / 2
    v1_circ = math.sqrt(mu / r1)
    v_apo = math.sqrt(mu * (2 / r2 - 1 / a_t))

    dv1 = abs(math.sqrt(mu * (2 / r1 - 1 / a_t)) - v1_circ)
    dv_plane = plane_change(v_apo, delta_i)
    dv2 = abs(math.sqrt(mu / r2) - v_apo)
    tof = math.pi * math.sqrt(a_t ** 3 / mu)

    return TransferResult(
        dv1=dv1,
        dv2=dv2 + dv_plane,
        total_dv=dv1 + dv2 + dv_plane,
        tof=tof,
        transfer_a=a_t,
        method="HOHMANN+PLANE_CHANGE",
        notes=f"plane change at apo: {dv_plane:.1f} m/s",
    )


def low_thrust_transfer(
    r1: float, r2: float, thrust_accel: float, mu: float = MU_EARTH
) -> TransferResult:
    """Rough exploratory low-thrust spiral estimate, not a trajectory optimizer."""
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    if not math.isfinite(thrust_accel) or thrust_accel < 0:
        raise ValueError("thrust_accel must be finite and non-negative")
    n = math.sqrt(mu / r1 ** 3)
    mass_ratio = math.exp(thrust_accel * math.log(r2 / r1) / (n ** 2 * r1))
    dv = thrust_accel * math.log(mass_ratio)

    a_t = (r1 + r2) / 2
    tof = math.sqrt(2 * (r2 - r1) ** 3 / (9 * mu)) if r2 > r1 else 0

    return TransferResult(
        dv1=dv,
        dv2=0,
        total_dv=dv,
        tof=tof,
        transfer_a=a_t,
        method="LOW_THRUST_SPIRAL_HEURISTIC",
        notes="exploratory heuristic; not optimized or flight-qualified",
    )




def hohmann_arrival_velocity(
    r1: float, r2: float, mu: float = MU_EARTH
) -> tuple[float, float]:
    """Arrival speed and circularization delta-v for a Hohmann transfer."""
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    a_t = (r1 + r2) / 2
    v_arrival = math.sqrt(mu * (2 / r2 - 1 / a_t))
    v_target = math.sqrt(mu / r2)
    return v_arrival, abs(v_arrival - v_target)


def launch_window_porkchop(
    r1: float,
    r2: float,
    synodic_period: float,
    phase_step: float = 15.0,
    tof_min: float = 1.0,
    tof_max: float = 200.0,
    mu: float = MU_EARTH,
) -> list[tuple[float, float, float]]:
    """Generate porkchop samples via repository-native Lambert costs.

    Returns list of (phase_deg, tof_days, total_dv). Not a mission-design
    product; research laboratory surface. ``synodic_period`` retained for API
    lineage and is not required for the two-body Lambert grid.
    """
    del synodic_period
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    if phase_step <= 0 or tof_max <= tof_min:
        return []

    results: list[tuple[float, float, float]] = []
    phase = 0.0
    while phase < 360.0:
        tof_days = tof_min
        while tof_days <= tof_max:
            tof_s = tof_days * 86400.0
            try:
                phase_rad = math.radians(phase)
                # avoid near-0 transfer angle singularity
                if abs(math.sin(phase_rad)) < 1e-3 and abs(math.cos(phase_rad) - 1.0) < 1e-3:
                    tof_days += 5.0
                    continue
                dv = lambert_transfer_cost(r1, r2, tof_s, mu=mu, phase_angle_rad=phase_rad)
                if math.isfinite(dv) and 0 < dv < 20000:
                    results.append((phase, tof_days, dv))
            except (ValueError, ZeroDivisionError, OverflowError):
                pass
            tof_days += 5.0
        phase += phase_step

    results.sort(key=lambda item: item[2])
    return results[:50]


def intercept_velocity(
    r1: float, r2: float, tof: float, mu: float = MU_EARTH
) -> tuple[float, float]:
    """Lambert-informed arrival speed and circularization delta-v.

    Places coplanar positions at 180 deg separation for a determinate geometry.
    For arbitrary phase use ``solve_lambert`` directly.
    """
    if not math.isfinite(tof) or tof <= 0:
        raise ValueError("tof must be finite and positive")
    _positive_radius(r1, "r1")
    _positive_radius(r2, "r2")
    _positive_radius(mu, "mu")
    from alpha.lambert import solve_lambert

    r1v = (r1, 0.0, 0.0)
    r2v = (-r2, 0.0, 0.0)
    sol = solve_lambert(r1v, r2v, tof, mu=mu, short_way=True)
    v_arrival = (sol.v2[0] ** 2 + sol.v2[1] ** 2 + sol.v2[2] ** 2) ** 0.5
    v_target = math.sqrt(mu / r2)
    return v_arrival, abs(v_arrival - v_target)

