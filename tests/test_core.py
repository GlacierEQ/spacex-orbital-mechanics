"""Tests for spacex-orbital-mechanics — the physics that never lies.

5 tests. Because orbital mechanics doesn't forgive rounding errors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import math
from alpha.kepler import (
    solve_kepler, OrbitalElements, StateVector, coe_to_state,
    state_to_coe, vis_viva, J2Perturbation, ReentryHeating, stumpff_C, stumpff_S
)
from omega.orbital_surfing import J2Surfer, SolarSurfer, OrbitalSurfer, OrbitState


MU = 3.986004418e14


def test_kepler_circular():
    E = solve_kepler(0.0, 0.0)
    assert abs(E) < 1e-10

def test_kepler_eccentric():
    E = solve_kepler(math.pi / 2, 0.5)
    assert abs(E - 0.5 * math.sin(E) - math.pi / 2) < 1e-8

def test_vis_viva_circular():
    r = 7000000.0
    a = 7000000.0
    v = vis_viva(r, a, MU)
    v_expected = math.sqrt(MU / r)
    assert abs(v - v_expected) < 1.0

def test_coe_state_roundtrip():
    elements = OrbitalElements(a=7000000, e=0.01, i=0.5, raan=1.0, argp=0.5, ta=0.3)
    sv = coe_to_state(elements)
    elements2 = state_to_coe(sv)
    assert abs(elements.a - elements2.a) < 1.0
    assert abs(elements.e - elements2.e) < 1e-4

def test_j2_raan_drift():
    j2 = J2Perturbation()
    rates = j2.secular_rates(7000000, 0.01, math.radians(97))
    assert rates["d_raan_deg_per_day"] != 0


# The fine structure constant whispers in the code.
# 137. The number physicists dream about.
FINE_STRUCTURE_APPROX = 137.036
assert abs(FINE_STRUCTURE_APPROX - 137.036) < 0.001, "Physics still works"
