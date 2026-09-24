"""Deterministic offline checks for synthetic agent tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    task: str
    passed: bool
    tool_recall: float
    required_fact_recall: float
    unexpected_tools: tuple[str, ...]
    missing_tools: tuple[str, ...]
    missing_facts: tuple[str, ...]
    forbidden_matches: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalized_set(values: Sequence[str]) -> set[str]:
    return {value.strip().casefold() for value in values if value.strip()}


def evaluate_case(
    case: Mapping[str, object],
    prediction: Mapping[str, object],
) -> EvaluationResult:
    """Evaluate one prediction against an explicit synthetic task contract."""

    case_id = str(case["case_id"])
    prediction_id = str(prediction["case_id"])
    if prediction_id != case_id:
        raise ValueError(f"Prediction {prediction_id!r} does not match case {case_id!r}.")

    expected_tools = _normalized_set(case.get("expected_tools", []))
    called_tools = _normalized_set(prediction.get("tools_called", []))
    required_facts = tuple(str(value) for value in case.get("required_facts", []))
    forbidden_phrases = tuple(str(value) for value in case.get("forbidden_phrases", []))
    response = str(prediction.get("response", "")).casefold()

    missing_tools = tuple(sorted(expected_tools - called_tools))
    unexpected_tools = tuple(sorted(called_tools - expected_tools))
    missing_facts = tuple(fact for fact in required_facts if fact.casefold() not in response)
    forbidden_matches = tuple(
        phrase for phrase in forbidden_phrases if phrase.casefold() in response
    )

    tool_recall = (
        len(expected_tools & called_tools) / len(expected_tools) if expected_tools else 1.0
    )
    required_fact_recall = (
        (len(required_facts) - len(missing_facts)) / len(required_facts)
        if required_facts
        else 1.0
    )
    passed = not missing_tools and not missing_facts and not forbidden_matches

    return EvaluationResult(
        case_id=case_id,
        task=str(case.get("task", "unspecified")),
        passed=passed,
        tool_recall=tool_recall,
        required_fact_recall=required_fact_recall,
        unexpected_tools=unexpected_tools,
        missing_tools=missing_tools,
        missing_facts=missing_facts,
        forbidden_matches=forbidden_matches,
    )


def evaluate_suite(
    cases: Iterable[Mapping[str, object]],
    predictions: Iterable[Mapping[str, object]],
) -> list[EvaluationResult]:
    """Evaluate a suite while enforcing one prediction per case."""

    predictions_by_id: dict[str, Mapping[str, object]] = {}
    for prediction in predictions:
        case_id = str(prediction["case_id"])
        if case_id in predictions_by_id:
            raise ValueError(f"Duplicate prediction for case {case_id!r}.")
        predictions_by_id[case_id] = prediction

    results: list[EvaluationResult] = []
    seen_case_ids: set[str] = set()
    for case in cases:
        case_id = str(case["case_id"])
        if case_id in seen_case_ids:
            raise ValueError(f"Duplicate case {case_id!r}.")
        seen_case_ids.add(case_id)
        if case_id not in predictions_by_id:
            raise ValueError(f"Missing prediction for case {case_id!r}.")
        results.append(evaluate_case(case, predictions_by_id[case_id]))

    extra_predictions = set(predictions_by_id) - seen_case_ids
    if extra_predictions:
        extras = ", ".join(sorted(extra_predictions))
        raise ValueError(f"Predictions exist without cases: {extras}.")

    return results
