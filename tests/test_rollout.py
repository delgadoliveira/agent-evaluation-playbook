import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_eval_playbook.rollout import assess_ring, wilson_lower_bound


class RolloutTests(unittest.TestCase):
    def test_holds_on_critical_failure(self) -> None:
        result = assess_ring(
            ring="preview",
            successes=490,
            total=500,
            critical_failures=1,
            target_rate=0.90,
            minimum_samples=400,
        )

        self.assertEqual(result.recommendation, "hold")

    def test_continues_below_minimum_samples(self) -> None:
        result = assess_ring(
            ring="early",
            successes=95,
            total=100,
            critical_failures=0,
            target_rate=0.85,
            minimum_samples=200,
        )

        self.assertEqual(result.recommendation, "continue")

    def test_wilson_bound_is_below_observed_rate(self) -> None:
        lower = wilson_lower_bound(90, 100)

        self.assertGreater(lower, 0.0)
        self.assertLess(lower, 0.90)


if __name__ == "__main__":
    unittest.main()
