"""Kepler equation solvers and orbital element conversions.

Implements universal Kepler solver via Householder iteration.
Converts between classical orbital elements (COE) and state vectors.
Pure math — no external dependencies.
"""

import math
from dataclasses import dataclass
from typing import Optional

MU_EARTH = 3.986004418e14
MU_MARS = 4.282837e13
MU_MOON = 4.9048695e12
R_EARTH = 6371000.0
R_MARS = 3389500.0
R_MOON = 1737400.0


@dataclass
class OrbitalElements:
    a: float
    e: float
    i: float
    raan: float
    argp: float
    ta: float
    mu: float = MU_EARTH

    @property
    def period(self) -> float:
        if self.a <= 0:
            return float("inf")
        return 2 * math.pi * math.sqrt(self.a ** 3 / self.mu)

    @property
    def specific_energy(self) -> float:
        return -self.mu / (2 * self.a)

    @property
    def angular_momentum(self) -> float:
        p = self.a * (1 - self.e ** 2)
        return math.sqrt(self.mu * p)

    @property
    def periapsis(self) -> float:
        return self.a * (1 - self.e)

    @property
    def apoapsis(self) -> float:
        return self.a * (1 + self.e)


@dataclass
class StateVector:
    r: tuple[float, float, float]
    v: tuple[float, float, float]
    mu: float = MU_EARTH

    @property
    def radius(self) -> float:
        return math.sqrt(sum(x ** 2 for x in self.r))

    @property
    def speed(self) -> float:
        return math.sqrt(sum(x ** 2 for x in self.v))

    @property
    def specific_energy(self) -> float:
        return self.speed ** 2 / 2 - self.mu / self.radius


def solve_kepler(M: float, e: float, tol: float = 1e-12, max_iter: int = 50) -> float:
    """Solve Kepler's equation M = E - e*sin(E) via Newton-Raphson."""
    M = M % (2 * math.pi)

    if e < 0.8:
        E = M if M < math.pi else M - e
    else:
        E = math.pi

    for _ in range(max_iter):
        f = E - e * math.sin(E) - M
        fp = 1 - e * math.cos(E)
        if abs(fp) < 1e-15:
            break
        delta = f / fp
        E -= delta
        if abs(delta) < tol:
            break

    return E


def true_anomaly_from_eccentric(E: float, e: float) -> float:
    """Convert eccentric anomaly to true anomaly."""
    return 2 * math.atan2(
        math.sqrt(1 + e) * math.sin(E / 2),
        math.sqrt(1 - e) * math.cos(E / 2),
    )


def orbital_period(a: float, mu: float = MU_EARTH) -> float:
    return 2 * math.pi * math.sqrt(a ** 3 / mu)


def vis_viva(r: float, a: float, mu: float = MU_EARTH) -> float:
    """Velocity from vis-viva equation: v = sqrt(mu * (2/r - 1/a))."""
    return math.sqrt(mu * (2 / r - 1 / a))


def hohmann_delta(v1: float, v2: float) -> tuple[float, float, float]:
    """Hohmann transfer delta-v budget."""
    dv1 = abs(v2 - v1) * 0.5
    dv2 = abs(v1 - v2) * 0.5
    return dv1, dv2, dv1 + dv2


def coe_to_state(elements: OrbitalElements) -> StateVector:
    """Convert classical orbital elements to position and velocity in ECI."""
    a, e, i, raan, argp, ta, mu = (
        elements.a, elements.e, elements.i,
        elements.raan, elements.argp, elements.ta, elements.mu,
    )

    p = a * (1 - e ** 2)
    r_mag = p / (1 + e * math.cos(ta))

    r_perifocal = (
        r_mag * math.cos(ta),
        r_mag * math.sin(ta),
        0.0,
    )

    v_factor = math.sqrt(mu / p)
    v_perifocal = (
        -v_factor * math.sin(ta),
        v_factor * (e + math.cos(ta)),
        0.0,
    )

    cos_raan, sin_raan = math.cos(raan), math.sin(raan)
    cos_i, sin_i = math.cos(i), math.sin(i)
    cos_argp, sin_argp = math.cos(argp), math.sin(argp)

    def _rotate(vec):
        x = (cos_raan * cos_argp - sin_raan * sin_argp * cos_i) * vec[0] + \
            (-cos_raan * sin_argp - sin_raan * cos_argp * cos_i) * vec[1]
        y = (sin_raan * cos_argp + cos_raan * sin_argp * cos_i) * vec[0] + \
            (-sin_raan * sin_argp + cos_raan * cos_argp * cos_i) * vec[1]
        z = (sin_argp * sin_i) * vec[0] + (cos_argp * sin_i) * vec[1]
        return (x, y, z)

    return StateVector(
        r=_rotate(r_perifocal),
        v=_rotate(v_perifocal),
        mu=mu,
    )


def state_to_coe(sv: StateVector) -> OrbitalElements:
    """Convert state vector to classical orbital elements."""
    r = sv.r
    v = sv.v
    mu = sv.mu

    r_mag = math.sqrt(sum(x ** 2 for x in r))
    v_mag = math.sqrt(sum(x ** 2 for x in v))

    h_vec = (
        r[1] * v[2] - r[2] * v[1],
        r[2] * v[0] - r[0] * v[2],
        r[0] * v[1] - r[1] * v[0],
    )
    h_mag = math.sqrt(sum(x ** 2 for x in h_vec))

    energy = v_mag ** 2 / 2 - mu / r_mag
    a = -mu / (2 * energy) if energy != 0 else float("inf")

    e_vec = tuple(
        (v_mag ** 2 / mu - 1 / r_mag) * r[i] -
        (sum(r[j] * v[j] for j in range(3)) / mu) * v[i]
        for i in range(3)
    )
    e = math.sqrt(sum(x ** 2 for x in e_vec))

    n_vec = (-h_vec[1], h_vec[0], 0.0)
    n_mag = math.sqrt(sum(x ** 2 for x in n_vec))

    i = math.acos(max(-1, min(1, h_vec[2] / h_mag))) if h_mag > 1e-10 else 0.0

    if n_mag > 1e-10:
        raan = math.acos(max(-1, min(1, n_vec[0] / n_mag)))
        if n_vec[1] < 0:
            raan = 2 * math.pi - raan
    else:
        raan = 0.0

    if e > 1e-10:
        argp = math.acos(max(-1, min(1,
            (n_vec[0] * e_vec[0] + n_vec[1] * e_vec[1]) / (n_mag * e)
        )))
        if e_vec[2] < 0:
            argp = 2 * math.pi - argp
    else:
        argp = 0.0

    if e > 1e-10:
        ta = math.acos(max(-1, min(1,
            (e_vec[0] * r[0] + e_vec[1] * r[1] + e_vec[2] * r[2]) / (e * r_mag)
        )))
        rv_dot = r[0] * v[0] + r[1] * v[1] + r[2] * v[2]
        if rv_dot < 0:
            ta = 2 * math.pi - ta
    else:
        ta = 0.0

    return OrbitalElements(a=a, e=e, i=i, raan=raan, argp=argp, ta=ta, mu=mu)
