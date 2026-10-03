"""Guard against false success from upstream testbench $finish behavior."""
import unittest
from checks import check_simulation


class SimulationAcceptance(unittest.TestCase):
    def test_complete(self):
        check_simulation("FINAL RESULTS: 36 PASSED, 0 FAILED", 0)

    def test_failures_returning_zero(self):
        for output in ["!! GLOBAL WATCHDOG TIMEOUT !!",
                       "FINAL RESULTS: 35 PASSED, 1 FAILED",
                       "FINAL RESULTS: 0 PASSED, 0 FAILED",
                       "[FAIL] row 0\nFINAL RESULTS: 36 PASSED, 0 FAILED",
                       "STARTING TESTS", ""]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                check_simulation(output, 0)

    def test_runtime_crash_after_summary(self):
        with self.assertRaises(ValueError):
            check_simulation("FINAL RESULTS: 36 PASSED, 0 FAILED", 1)

    def test_concatenated_stale_logs(self):
        with self.assertRaises(ValueError):
            check_simulation("FINAL RESULTS: 36 PASSED, 0 FAILED\n" * 2, 0)


if __name__ == "__main__":
    unittest.main()
