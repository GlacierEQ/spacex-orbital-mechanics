"""Repository-native Lambert boundary-value solver (two-body).

This is a real numerical Lambert solver for research and laboratory use.
It is not a flight-dynamics authority, not production mission design software,
and is not affiliated with SpaceX.

Method: universal-variable Lambert (Battin/Vallado style) for two position
vectors and time-of-flight in a Keplerian two-body field.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from alpha.kepler import MU_EARTH, stumpff_C, stumpff_S

EVIDENCE_STATE = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"
SOLVER_IDENTITY = "REPOSITORY_NATIVE_LAMBERT_TWO_BODY"


@dataclass(frozen=True)
class LambertSolution:
    v1: tuple[float, float, float]
    v2: tuple[float, float, float]
    a: float
    tof: float
    turns: int
    short_way: bool
    residual: float
    method: str = SOLVER_IDENTITY
    evidence: str = EVIDENCE_STATE


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a: tuple[float, float, float]) -> float:
    return math.sqrt(_dot(a, a))


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _scale(a: tuple[float, float, float], s: float) -> tuple[float, float, float]:
    return (a[0] * s, a[1] * s, a[2] * s)


def _add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _unit(a: tuple[float, float, float]) -> tuple[float, float, float]:
    n = _norm(a)
    if n <= 0.0 or not math.isfinite(n):
        raise ValueError("zero or non-finite vector")
    return _scale(a, 1.0 / n)


def solve_lambert(
    r1: tuple[float, float, float],
    r2: tuple[float, float, float],
    tof: float,
    *,
    mu: float = MU_EARTH,
    short_way: bool = True,
    turns: int = 0,
    tol: float = 1e-8,
    max_iter: int = 80,
) -> LambertSolution:
    """Solve Lambert's problem for velocities at r1 and r2 given TOF.

    Parameters are SI meters / seconds. Multi-revolution support is limited to
    ``turns`` revolutions with a simple bracket on the universal variable.
    """
    if tof <= 0 or not math.isfinite(tof):
        raise ValueError("tof must be finite and positive")
    if mu <= 0 or not math.isfinite(mu):
        raise ValueError("mu must be finite and positive")
    if turns < 0:
        raise ValueError("turns must be >= 0")

    r1_mag = _norm(r1)
    r2_mag = _norm(r2)
    if r1_mag <= 0 or r2_mag <= 0:
        raise ValueError("position magnitudes must be positive")

    cos_dnu = _dot(r1, r2) / (r1_mag * r2_mag)
    cos_dnu = max(-1.0, min(1.0, cos_dnu))
    # For near-180° transfers the chord geometry is singular in the classic A
    # formulation. Nudge r2 by a tiny out-of-plane component to define a plane
    # without materially changing the boundary-value problem for laboratory use.
    r2_work = r2
    h = _cross(r1, r2)
    if _norm(h) < 1e-8 * r1_mag * r2_mag:
        ref = (0.0, 0.0, 1.0) if abs(r1[2]) / r1_mag < 0.9 else (0.0, 1.0, 0.0)
        nudge = _scale(_unit(_cross(r1, ref)), 1e-6 * r2_mag)
        r2_work = _add(r2, nudge)
        # renormalize to original magnitude
        r2_work = _scale(_unit(r2_work), r2_mag)
        cos_dnu = _dot(r1, r2_work) / (r1_mag * r2_mag)
        cos_dnu = max(-1.0, min(1.0, cos_dnu))
        h = _cross(r1, r2_work)

    sin_dnu = math.sqrt(max(0.0, 1.0 - cos_dnu * cos_dnu))
    if h[2] < 0:
        sin_dnu = -abs(sin_dnu) if short_way else abs(sin_dnu)
    else:
        sin_dnu = abs(sin_dnu) if short_way else -abs(sin_dnu)
    if not short_way and _norm(h) >= 1e-8 * r1_mag * r2_mag:
        # long-way: invert transfer angle sense
        sin_dnu = -sin_dnu
        cos_dnu = cos_dnu  # unchanged

    A = sin_dnu * math.sqrt(r1_mag * r2_mag / max(1e-16, 1.0 - cos_dnu))
    if abs(A) < 1e-14:
        raise ValueError("Lambert geometry is singular (A≈0)")
    r2 = r2_work

    def y_of_z(z: float) -> float:
        if abs(z) < 1e-12:
            return r1_mag + r2_mag + A * (z * stumpff_S(0.0) - 1.0)  # unused branch
        return r1_mag + r2_mag + A * (z * stumpff_S(z) - 1.0) / math.sqrt(stumpff_C(z))

    def tof_of_z(z: float) -> float:
        C = stumpff_C(z)
        S = stumpff_S(z)
        if C <= 0:
            return float("inf")
        y = r1_mag + r2_mag + A * (z * S - 1.0) / math.sqrt(C)
        if y < 0:
            return float("inf")
        x = math.sqrt(y / C)
        return (x ** 3 * S + A * math.sqrt(y)) / math.sqrt(mu)

    # bracket z
    z = 0.0
    if turns == 0:
        z_lo, z_hi = -0.25 * math.pi ** 2 + 1e-6, 4.0 * math.pi ** 2
    else:
        z_lo = (2 * turns * math.pi) ** 2 + 1e-6
        z_hi = (2 * (turns + 1) * math.pi) ** 2 - 1e-6

    # expand high if needed
    f_lo = tof_of_z(z_lo) - tof
    f_hi = tof_of_z(z_hi) - tof
    expand = 0
    while f_lo * f_hi > 0 and expand < 40:
        z_hi *= 1.5
        f_hi = tof_of_z(z_hi) - tof
        expand += 1
    if f_lo * f_hi > 0:
        # fallback bisection around 0
        z_lo, z_hi = -4.0, 40.0
        f_lo, f_hi = tof_of_z(z_lo) - tof, tof_of_z(z_hi) - tof

    for _ in range(max_iter):
        z = 0.5 * (z_lo + z_hi)
        f = tof_of_z(z) - tof
        if abs(f) < tol * max(1.0, tof):
            break
        if f_lo * f <= 0:
            z_hi = z
            f_hi = f
        else:
            z_lo = z
            f_lo = f

    C = stumpff_C(z)
    S = stumpff_S(z)
    y = r1_mag + r2_mag + A * (z * S - 1.0) / math.sqrt(C)
    if y <= 0:
        raise ValueError("Lambert failed to converge to physical y")
    f_lag = 1.0 - y / r1_mag
    g_lag = A * math.sqrt(y / mu)
    gdot = 1.0 - y / r2_mag
    if abs(g_lag) < 1e-16:
        raise ValueError("Lambert g-lagrange near zero")

    v1 = _scale(_sub(r2, _scale(r1, f_lag)), 1.0 / g_lag)
    v2 = _scale(_sub(_scale(r2, gdot), r1), 1.0 / g_lag)

    # semi-major axis from energy at departure
    v1s = _norm(v1)
    energy = v1s * v1s / 2.0 - mu / r1_mag
    a = float("inf") if abs(energy) < 1e-18 else -mu / (2.0 * energy)

    residual = abs(tof_of_z(z) - tof)
    return LambertSolution(
        v1=v1,
        v2=v2,
        a=a,
        tof=tof,
        turns=turns,
        short_way=short_way,
        residual=residual,
    )


def lambert_transfer_cost(
    r1_mag: float,
    r2_mag: float,
    tof: float,
    *,
    mu: float = MU_EARTH,
    phase_angle_rad: float = math.pi,
) -> float:
    """Scalar total Δv estimate using coplanar circular departure/arrival.

    Places r1 on +x and r2 at ``phase_angle_rad`` in the xy-plane.
    """
    if r1_mag <= 0 or r2_mag <= 0:
        raise ValueError("radii must be positive")
    r1 = (r1_mag, 0.0, 0.0)
    r2 = (r2_mag * math.cos(phase_angle_rad), r2_mag * math.sin(phase_angle_rad), 0.0)
    sol = solve_lambert(r1, r2, tof, mu=mu, short_way=True)
    v1_circ = math.sqrt(mu / r1_mag)
    v2_circ = math.sqrt(mu / r2_mag)
    # circular velocity along +y at r1 and along tangent at r2
    v1c = (0.0, v1_circ, 0.0)
    t_hat = (-math.sin(phase_angle_rad), math.cos(phase_angle_rad), 0.0)
    v2c = _scale(t_hat, v2_circ)
    dv1 = _norm(_sub(sol.v1, v1c))
    dv2 = _norm(_sub(v2c, sol.v2))
    return dv1 + dv2
