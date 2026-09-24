import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_eval_playbook.experiments import analyze_binary_experiment


class ExperimentTests(unittest.TestCase):
    def test_reports_positive_effect_and_guardrail(self) -> None:
        result = analyze_binary_experiment(
            control_successes=730,
            control_total=1000,
            treatment_successes=780,
            treatment_total=1000,
            guardrail_control_events=20,
            guardrail_control_total=1000,
            guardrail_treatment_events=15,
            guardrail_treatment_total=1000,
            guardrail_margin=0.01,
        )

        self.assertGreater(result.absolute_effect, 0.0)
        self.assertLess(result.confidence_low, result.confidence_high)
        self.assertTrue(result.guardrail_non_inferior)

    def test_rejects_invalid_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "between zero and total"):
            analyze_binary_experiment(
                control_successes=11,
                control_total=10,
                treatment_successes=8,
                treatment_total=10,
                guardrail_control_events=1,
                guardrail_control_total=10,
                guardrail_treatment_events=1,
                guardrail_treatment_total=10,
                guardrail_margin=0.01,
            )


if __name__ == "__main__":
    unittest.main()
