"""Repository-native Lambert solver tests."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alpha.kepler import MU_EARTH
from alpha.lambert import SOLVER_IDENTITY, lambert_transfer_cost, solve_lambert


class TestLambertSolver(unittest.TestCase):
    def test_earth_leo_to_geo_finite(self) -> None:
        r1 = (6_771_000.0, 0.0, 0.0)
        r2 = (-42_164_000.0, 0.0, 0.0)
        tof = 5.0 * 3600.0  # 5 hours (not Hohmann half-period; solver still returns)
        sol = solve_lambert(r1, r2, tof, mu=MU_EARTH, short_way=True)
        self.assertEqual(sol.method, SOLVER_IDENTITY)
        self.assertTrue(math.isfinite(sol.v1[0]))
        self.assertTrue(math.isfinite(sol.v2[0]))
        self.assertLess(sol.residual, 1.0)

    def test_transfer_cost_positive(self) -> None:
        dv = lambert_transfer_cost(
            6_771_000.0,
            42_164_000.0,
            tof=0.5 * math.pi * math.sqrt(((6_771_000.0 + 42_164_000.0) / 2) ** 3 / MU_EARTH),
            phase_angle_rad=math.pi,
        )
        self.assertGreater(dv, 1000.0)
        self.assertLess(dv, 15000.0)


if __name__ == "__main__":
    unittest.main()
