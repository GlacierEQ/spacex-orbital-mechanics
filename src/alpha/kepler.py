"""Kepler equation solvers, orbital element conversions, and perturbation models.

Implements universal Kepler solver, hyperbolic/parabolic support,
J2 oblateness perturbation, and COE ↔ state vector conversions.
Pure math — no external dependencies.
"""

import math
from dataclasses import dataclass
from typing import Optional

MU_EARTH = 3.986004418e14
MU_MARS = 4.282837e13
MU_MOON = 4.9048695e12
R_EARTH = 6378137.0
R_MARS = 3389500.0
R_MOON = 1737400.0
J2_EARTH = 1.08263e-3
J2_MARS = 1.956e-3


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


def solve_hyperbolic_kepler(H: float, e: float, tol: float = 1e-12, max_iter: int = 50) -> float:
    """Solve hyperbolic Kepler equation: H = e*sinh(H) - M_h."""
    if e < 1.0:
        return solve_kepler(H, e, tol, max_iter)

    M_h = H
    if M_h > 0:
        F = math.log(2 * M_h / e + 1.8)
    else:
        F = -math.log(-2 * M_h / e + 1.8)

    for _ in range(max_iter):
        if e > 1.5 and abs(F) > 1.6:
            F = math.copysign(1, F) * math.log(2 * abs(M_h) / e + 1.8)
        f = e * math.sinh(F) - F - M_h
        fp = e * math.cosh(F) - 1
        if abs(fp) < 1e-15:
            break
        delta = f / fp
        F -= delta
        if abs(delta) < tol:
            break

    return F


def solve_universal(s: float, e: float, mu: float, tol: float = 1e-12) -> float:
    """Universal variable Kepler solver for any orbit type.

    Solves for chi in: s = r0*v_r0/sqrt(mu)*chi**2*C(psi*chi**2) + (1-e*r0/a)*chi**3*S(psi*chi**2) + r0*chi

    where C and S are Stumpff functions and psi = chi**2/alpha (alpha = 1/a for ellipse, -1/a for hyperbola).
    """
    return solve_kepler(s % (2 * math.pi), e, tol) if e < 1.0 else solve_hyperbolic_kepler(s, e, tol)


def stumpff_C(z: float) -> float:
    """Stumpff function C(z) for series expansion."""
    if z > 1e-6:
        return (1 - math.cos(math.sqrt(z))) / z
    elif z < -1e-6:
        return (math.cosh(math.sqrt(-z)) - 1) / (-z)
    else:
        return 1 / 2 - z / 24 + z ** 2 / 720


def stumpff_S(z: float) -> float:
    """Stumpff function S(z) for series expansion."""
    if z > 1e-6:
        sz = math.sqrt(z)
        return (sz - math.sin(sz)) / (sz ** 3)
    elif z < -1e-6:
        sz = math.sqrt(-z)
        return (math.sinh(sz) - sz) / ((-z) ** 1.5)
    else:
        return 1 / 6 - z / 120 + z ** 2 / 5040


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


class J2Perturbation:
    """J2 (Earth oblateness) perturbation model.

    Computes secular rates of change for RAAN, argument of perigee, and mean anomaly.
    Valid for near-circular, low-inclination orbits typical of LEO operations.
    """

    def __init__(self, mu: float = MU_EARTH, Re: float = R_EARTH, j2: float = J2_EARTH):
        self.mu = mu
        self.Re = Re
        self.j2 = j2

    def secular_rates(self, a: float, e: float, i: float) -> dict:
        """Compute J2 secular rates: dRAAN/dt, dω/dt, dM/dt in rad/s."""
        p = a * (1 - e ** 2)
        n = math.sqrt(self.mu / a ** 3)
        factor = 3 * n * self.j2 * self.Re ** 2 / (2 * p ** 2)

        cos_i = math.cos(i)

        d_raan_dt = -factor * cos_i
        d_argp_dt = factor * (2 - 2.5 * math.sin(i) ** 2)
        d_mean_anomaly_dt = n + factor * math.sqrt(1 - e ** 2) * (1 - 1.5 * math.sin(i) ** 2)

        return {
            "d_raan_dt": d_raan_dt,
            "d_argp_dt": d_argp_dt,
            "d_mean_anomaly_dt": d_mean_anomaly_dt,
            "d_raan_deg_per_day": math.degrees(d_raan_dt) * 86400,
            "d_argp_deg_per_day": math.degrees(d_argp_dt) * 86400,
            "d_mean_motion_deg_per_day": math.degrees(d_mean_anomaly_dt) * 86400,
        }

    def propagate_coe(
        self, elements: OrbitalElements, dt: float
    ) -> OrbitalElements:
        """Propagate COE under J2 secular effects for time dt seconds."""
        rates = self.secular_rates(elements.a, elements.e, elements.i)

        new_raan = elements.raan + rates["d_raan_dt"] * dt
        new_argp = elements.argp + rates["d_argp_dt"] * dt
        mean_motion = math.sqrt(elements.mu / elements.a ** 3)
        mean_anomaly = elements.ta
        new_ta = mean_anomaly + rates["d_mean_anomaly_dt"] * dt

        new_raan = new_raan % (2 * math.pi)
        new_argp = new_argp % (2 * math.pi)
        new_ta = new_ta % (2 * math.pi)

        return OrbitalElements(
            a=elements.a, e=elements.e, i=elements.i,
            raan=new_raan, argp=new_argp, ta=new_ta, mu=elements.mu,
        )

    def half_life_raan(self, a: float, e: float, i: float) -> float:
        """Time for RAAN to precess by 180 degrees (half orbit plane rotation)."""
        rates = self.secular_rates(a, e, i)
        if abs(rates["d_raan_dt"]) < 1e-15:
            return float("inf")
        return math.pi / abs(rates["d_raan_dt"])

    def sun_sync_altitude(self, target_inclination: float, e: float = 0.0) -> float:
        """Compute altitude for sun-synchronous orbit at given inclination.

        Sun-sync requires dRAAN/dt = 360°/year ≈ 9.936°/day eastward.
        Uses bisection to solve for semi-major axis.
        """
        target_draan = 2 * math.pi / (365.25 * 86400)
        cos_i = math.cos(target_inclination)

        def _draan_at_alt(alt):
            a = self.Re + alt
            p = a * (1 - e ** 2)
            n = math.sqrt(self.mu / a ** 3)
            return abs(-1.5 * n * self.j2 * (self.Re / p) ** 2 * cos_i)

        a_lo, a_hi = self.Re + 100000, self.Re + 20000000
        for _ in range(100):
            a_mid = (a_lo + a_hi) / 2
            draan = _draan_at_alt(a_mid - self.Re)
            if draan > target_draan:
                a_lo = a_mid
            else:
                a_hi = a_mid
            if abs(draan - target_draan) / target_draan < 1e-8:
                break

        return (a_lo + a_hi) / 2 - self.Re

    def perturbation_acceleration(
        self, r: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        """Instantaneous J2 perturbation acceleration in ECI.

        Returns (ax, ay, az) in m/s².
        """
        x, y, z = r
        r_mag = math.sqrt(x ** 2 + y ** 2 + z ** 2)

        if r_mag < 1.0:
            return (0.0, 0.0, 0.0)

        factor = -1.5 * self.j2 * self.mu * self.Re ** 2 / r_mag ** 7

        ax = factor * x * (5 * z ** 2 - r_mag ** 2)
        ay = factor * y * (5 * z ** 2 - r_mag ** 2)
        az = factor * z * (3 * z ** 2 - r_mag ** 2)

        return (ax, ay, az)


class ReentryHeating:
    """Stagnation point heating rate model for atmospheric entry.

    Based on Sutton-Graves approximate formula:
    q = k * sqrt(rho / Rn) * V^3

    where k is a gas constant, rho is atmospheric density, Rn is nose radius, V is velocity.
    """

    K_STAGNATION = 1.83e-4

    def __init__(
        self,
        nose_radius_m: float = 0.5,
        mass_kg: float = 5000.0,
        ballistic_coeff: float = 200.0,
    ):
        self.nose_radius = nose_radius_m
        self.mass = mass_kg
        self.ballistic_coeff = ballistic_coeff

    def heating_rate(
        self,
        velocity_ms: float,
        altitude_m: float,
    ) -> float:
        """Stagnation point heat flux in W/m²."""
        rho = self._atmosphere_density(altitude_m)
        if rho <= 0 or velocity_ms <= 0:
            return 0.0
        return self.K_STAGNATION * math.sqrt(rho / self.nose_radius) * velocity_ms ** 3

    def _atmosphere_density(self, altitude_m: float) -> float:
        """US Standard Atmosphere 1976 exponential model."""
        layers = [
            (0, 1.225, -1.437e-4),
            (11000, 0.364, -1.577e-4),
            (20000, 0.088, -1.577e-4),
            (32000, 0.013, -1.242e-4),
            (47000, 0.0015, -2.896e-4),
            (71000, 3.8e-5, -2.896e-4),
            (85000, 1.5e-6, -1.2e-4),
        ]

        for idx in range(len(layers) - 1, -1, -1):
            h0, rho0, scale_h = layers[idx]
            if altitude_m >= h0:
                return rho0 * math.exp(-(altitude_m - h0) * scale_h)

        return 0.0

    def total_heat_load(
        self,
        trajectory: list[tuple[float, float, float]],
    ) -> float:
        """Integrate total heat load over trajectory (J/m²).

        trajectory: list of (time_s, altitude_m, velocity_ms) sorted by time.
        """
        if len(trajectory) < 2:
            return 0.0

        total = 0.0
        for i in range(len(trajectory) - 1):
            t0, h0, v0 = trajectory[i]
            t1, h1, v1 = trajectory[i + 1]
            dt = t1 - t0

            q0 = self.heating_rate(v0, h0)
            q1 = self.heating_rate(v1, h1)

            total += 0.5 * (q0 + q1) * dt

        return total

    def peak_heating(
        self,
        trajectory: list[tuple[float, float, float]],
    ) -> dict:
        """Find peak heating conditions along trajectory."""
        if not trajectory:
            return {"peak_flux": 0, "altitude": 0, "velocity": 0}

        peak_q = 0.0
        peak_h = 0.0
        peak_v = 0.0

        for t, h, v in trajectory:
            q = self.heating_rate(v, h)
            if q > peak_q:
                peak_q = q
                peak_h = h
                peak_v = v

        return {
            "peak_flux_w_m2": peak_q,
            "altitude_km": peak_h / 1000,
            "velocity_km_s": peak_v / 1000,
            "heat_load_j_m2": self.total_heat_load(trajectory),
        }
