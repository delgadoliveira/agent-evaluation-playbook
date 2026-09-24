import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_eval_playbook.offline import evaluate_case, evaluate_suite


class OfflineEvaluationTests(unittest.TestCase):
    def test_passes_complete_prediction(self) -> None:
        case = {
            "case_id": "one",
            "task": "lookup",
            "expected_tools": ["search"],
            "required_facts": ["result 42"],
            "forbidden_phrases": ["invented"],
        }
        prediction = {
            "case_id": "one",
            "tools_called": ["search"],
            "response": "The answer is result 42.",
        }

        result = evaluate_case(case, prediction)

        self.assertTrue(result.passed)
        self.assertEqual(result.tool_recall, 1.0)
        self.assertEqual(result.required_fact_recall, 1.0)

    def test_diagnoses_missing_tool_and_fact(self) -> None:
        case = {
            "case_id": "one",
            "task": "lookup",
            "expected_tools": ["search", "verify"],
            "required_facts": ["result 42"],
            "forbidden_phrases": [],
        }
        prediction = {
            "case_id": "one",
            "tools_called": ["search"],
            "response": "I found a possible answer.",
        }

        result = evaluate_case(case, prediction)

        self.assertFalse(result.passed)
        self.assertEqual(result.missing_tools, ("verify",))
        self.assertEqual(result.missing_facts, ("result 42",))

    def test_rejects_extra_prediction(self) -> None:
        cases = [{"case_id": "one"}]
        predictions = [{"case_id": "one"}, {"case_id": "two"}]

        with self.assertRaisesRegex(ValueError, "without cases"):
            evaluate_suite(cases, predictions)


if __name__ == "__main__":
    unittest.main()
