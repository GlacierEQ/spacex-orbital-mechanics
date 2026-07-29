"""Test suite for SpaceX Lambert Solver."""
import unittest, math

class LambertSolverSim:
    def compute_delta_v(self, r1_km: float, r2_km: float) -> float:
        mu = 398600.4418
        sma = (r1_km + r2_km) / 2.0
        return math.sqrt(mu * (2.0 / r1_km - 1.0 / sma))

class TestLambertSolver(unittest.TestCase):
    def test_transfer_dv(self):
        s = LambertSolverSim()
        dv = s.compute_delta_v(6771.0, 42164.0)
        self.assertGreater(dv, 5.0)

if __name__ == "__main__":
    unittest.main()
