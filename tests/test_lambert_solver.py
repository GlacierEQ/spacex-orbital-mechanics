"""Historical-filename transfer-speed reference test.

This does not test a Lambert boundary-value solver. The repository's admitted
orbital proof is exercised by test_orbital.py and test_public_truth.py.
"""

import math
import unittest


class TransferSpeedReference:
    def compute_departure_speed(self, r1_km: float, r2_km: float) -> float:
        mu = 398600.4418
        sma = (r1_km + r2_km) / 2.0
        return math.sqrt(mu * (2.0 / r1_km - 1.0 / sma))


class TestTransferSpeedReference(unittest.TestCase):
    def test_transfer_departure_speed(self) -> None:
        speed = TransferSpeedReference().compute_departure_speed(6771.0, 42164.0)
        self.assertGreater(speed, 5.0)
        self.assertLess(speed, 11.0)


if __name__ == "__main__":
    unittest.main()
