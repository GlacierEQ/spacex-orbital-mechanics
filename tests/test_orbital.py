"""Orbital mechanics tests."""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from alpha.kepler import (
    solve_kepler, true_anomaly_from_eccentric, OrbitalElements,
    StateVector, coe_to_state, state_to_coe, MU_EARTH, R_EARTH,
    vis_viva, orbital_period,
)
from omega.orbit_planner import (
    hohmann_transfer, bi_elliptic_transfer, plane_change,
    combined_plane_change, low_thrust_transfer,
)

TOL = 1e-6


def test_kepler_circular():
    M = math.pi / 4
    e = 0.0
    E = solve_kepler(M, e)
    assert abs(E - M) < TOL


def test_kepler_eccentric():
    M = 1.0
    e = 0.5
    E = solve_kepler(M, e)
    residual = E - e * math.sin(E) - M
    assert abs(residual) < 1e-10


def test_kepler_high_eccentric():
    M = 0.1
    e = 0.99
    E = solve_kepler(M, e)
    residual = E - e * math.sin(E) - M
    assert abs(residual) < 1e-8


def test_true_anomaly():
    E = math.pi / 2
    e = 0.5
    ta = true_anomaly_from_eccentric(E, e)
    assert 0 < ta < 2 * math.pi


def test_circular_orbit_state():
    elements = OrbitalElements(
        a=R_EARTH + 400000, e=0.0, i=0.0, raan=0.0, argp=0.0, ta=0.0
    )
    sv = coe_to_state(elements)
    r_mag = sv.radius
    expected_r = R_EARTH + 400000
    assert abs(r_mag - expected_r) < 1.0


def test_state_to_coe_roundtrip():
    original = OrbitalElements(
        a=7000000, e=0.01, i=0.5, raan=1.0, argp=0.3, ta=0.7
    )
    sv = coe_to_state(original)
    recovered = state_to_coe(sv)

    assert abs(recovered.a - original.a) < 1.0
    assert abs(recovered.e - original.e) < 1e-6
    assert abs(recovered.i - original.i) < 1e-4
    assert abs(recovered.raan - original.raan) < 1e-4


def test_vis_viva():
    r = R_EARTH + 400000
    a = R_EARTH + 400000
    v = vis_viva(r, a)
    expected = math.sqrt(MU_EARTH / r)
    assert abs(v - expected) < 1.0


def test_orbital_period():
    a = R_EARTH + 400000
    T = orbital_period(a)
    assert 5000 < T < 6000


def test_hohmann_leo_to_geo():
    r1 = R_EARTH + 400000
    r2 = R_EARTH + 35786000
    result = hohmann_transfer(r1, r2)
    assert result.dv1 > 0
    assert result.dv2 > 0
    assert result.total_dv < 5000
    assert result.tof > 10000


def test_hohmann_circular():
    r = R_EARTH + 400000
    result = hohmann_transfer(r, r)
    assert result.total_dv < 1.0


def test_bi_elliptic():
    r1 = R_EARTH + 400000
    r2 = R_EARTH + 35786000
    r3 = R_EARTH + 50000000
    result = bi_elliptic_transfer(r1, r2, r3)
    assert result.total_dv > 0
    assert "mid-burn" in result.notes


def test_plane_change():
    v = 7800
    dv = plane_change(v, math.radians(28.5))
    assert dv > 0
    assert dv < 5000


def test_low_thrust():
    r1 = R_EARTH + 400000
    r2 = R_EARTH + 1000000
    result = low_thrust_transfer(r1, r2, 0.01)
    assert result.total_dv > 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
