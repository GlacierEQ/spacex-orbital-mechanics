from __future__ import annotations
"""Orbit planner — Hohmann, bi-elliptic, and plane change transfers.

Computes optimal delta-v budgets and transfer windows.
Includes porkchop plot data generation for launch windows.
"""

import math
from dataclasses import dataclass
from typing import Optional

from alpha.kepler import (
    OrbitalElements,
    StateVector,
    MU_EARTH,
    R_EARTH,
    orbital_period,
    vis_viva,
    state_to_coe,
    coe_to_state,
)


@dataclass
class TransferResult:
    dv1: float
    dv2: float
    total_dv: float
    tof: float
    transfer_a: float
    method: str
    notes: str = ""


def hohmann_transfer(r1: float, r2: float, mu: float = MU_EARTH) -> TransferResult:
    """Classic Hohmann transfer between circular orbits."""
    a_t = (r1 + r2) / 2

    v1_circ = math.sqrt(mu / r1)
    v2_circ = math.sqrt(mu / r2)
    v1_trans = math.sqrt(mu * (2 / r1 - 1 / a_t))
    v2_trans = math.sqrt(mu * (2 / r2 - 1 / a_t))

    dv1 = abs(v1_trans - v1_circ)
    dv2 = abs(v2_circ - v2_trans)
    tof = math.pi * math.sqrt(a_t ** 3 / mu)

    return TransferResult(
        dv1=dv1, dv2=dv2, total_dv=dv1 + dv2,
        tof=tof, transfer_a=a_t, method="HOHMANN",
    )


def bi_elliptic_transfer(
    r1: float, r2: float, r3: float, mu: float = MU_EARTH
) -> TransferResult:
    """Bi-elliptic transfer via intermediate orbit r3."""
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
        dv1=dv1, dv2=dv2, total_dv=dv1 + dv_mid + dv2,
        tof=tof1 + tof2, transfer_a=a1, method="BI-ELLIPTIC",
        notes=f"mid-burn dv={dv_mid:.1f} m/s via r3={r3:.0f} m",
    )


def plane_change(
    v: float, delta_i: float, fpa: float = 0.0
) -> float:
    """Plane change delta-v: dv = 2*v*sin(delta_i/2)*cos(fpa)."""
    return 2 * v * math.sin(delta_i / 2) * math.cos(fpa)


def combined_plane_change(
    r1: float, r2: float, delta_i: float, mu: float = MU_EARTH
) -> TransferResult:
    """Hohmann + plane change at apoapsis (cheapest point)."""
    a_t = (r1 + r2) / 2
    v1_circ = math.sqrt(mu / r1)
    v_apo = math.sqrt(mu * (2 / r2 - 1 / a_t))

    dv1 = abs(math.sqrt(mu * (2 / r1 - 1 / a_t)) - v1_circ)
    dv_plane = plane_change(v_apo, delta_i)
    dv2 = abs(math.sqrt(mu / r2) - v_apo)

    tof = math.pi * math.sqrt(a_t ** 3 / mu)

    return TransferResult(
        dv1=dv1, dv2=dv2 + dv_plane, total_dv=dv1 + dv2 + dv_plane,
        tof=tof, transfer_a=a_t, method="HOHMANN+PLANE_CHANGE",
        notes=f"plane change at apo: {dv_plane:.1f} m/s",
    )


def low_thrust_transfer(
    r1: float, r2: float, thrust_accel: float, mu: float = MU_EARTH
) -> TransferResult:
    """Spiral transfer with constant low thrust (approximate)."""
    n = math.sqrt(mu / r1 ** 3)
    mass_ratio = math.exp(
        thrust_accel * math.log(r2 / r1) / (n ** 2 * r1)
    )
    dv = thrust_accel * math.log(mass_ratio)

    a_t = (r1 + r2) / 2
    tof = math.sqrt(2 * (r2 - r1) ** 3 / (9 * mu)) if r2 > r1 else 0

    return TransferResult(
        dv1=dv, dv2=0, total_dv=dv, tof=tof,
        transfer_a=a_t, method="LOW_THRUST_SPIRAL",
    )


def launch_window_porkchop(
    r1: float, r2: float,
    synodic_period: float,
    phase_step: float = 1.0,
    tof_min: float = 0,
    tof_max: float = 500,
    mu: float = MU_EARTH,
) -> list[tuple[float, float, float]]:
    """Generate porkchop plot data: (phase_angle, tof_days, total_dv)."""
    results = []
    phase_range = int(360 / phase_step)
    tof_range = int((tof_max - tof_min) * 2)

    for p_idx in range(phase_range):
        phase = p_idx * phase_step
        for t_idx in range(tof_range):
            tof_days = tof_min + t_idx * 0.5
            tof_s = tof_days * 86400

            a_t = (r1 + r2) / 2
            v1_circ = math.sqrt(mu / r1)
            v2_circ = math.sqrt(mu / r2)

            if tof_s > 0:
                v1_trans = math.sqrt(mu * (2 / r1 - 1 / a_t))
                v2_trans = math.sqrt(mu * (2 / r2 - 1 / a_t))
                dv = abs(v1_trans - v1_circ) + abs(v2_circ - v2_trans)
            else:
                continue

            if dv < 15000:
                results.append((phase, tof_days, dv))

    results.sort(key=lambda x: x[2])
    return results[:50]


def intercept_velocity(
    r1: float, r2: float, tof: float, mu: float = MU_EARTH
) -> tuple[float, float]:
    """Lambert-style intercept: arrival v at target orbit."""
    a_t = (r1 + r2) / 2
    v_arrival = math.sqrt(mu * (2 / r2 - 1 / a_t))
    v_target = math.sqrt(mu / r2)
    return v_arrival, abs(v_arrival - v_target)
