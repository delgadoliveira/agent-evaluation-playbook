"""Transparent statistical summaries for synthetic binary A/B experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist


@dataclass(frozen=True)
class ExperimentResult:
    control_rate: float
    treatment_rate: float
    absolute_effect: float
    confidence_low: float
    confidence_high: float
    guardrail_control_rate: float
    guardrail_treatment_rate: float
    guardrail_effect: float
    guardrail_non_inferior: bool


def _validate_count(successes: int, total: int, label: str) -> None:
    if total <= 0:
        raise ValueError(f"{label} total must be positive.")
    if successes < 0 or successes > total:
        raise ValueError(f"{label} successes must be between zero and total.")


def _difference_interval(
    control_successes: int,
    control_total: int,
    treatment_successes: int,
    treatment_total: int,
    confidence: float,
) -> tuple[float, float, float]:
    _validate_count(control_successes, control_total, "Control")
    _validate_count(treatment_successes, treatment_total, "Treatment")
    if not 0.0 < confidence < 1.0:
        raise ValueError("Confidence must be between zero and one.")

    control_rate = control_successes / control_total
    treatment_rate = treatment_successes / treatment_total
    effect = treatment_rate - control_rate
    standard_error = sqrt(
        control_rate * (1.0 - control_rate) / control_total
        + treatment_rate * (1.0 - treatment_rate) / treatment_total
    )
    z_value = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    return effect, effect - z_value * standard_error, effect + z_value * standard_error


def analyze_binary_experiment(
    *,
    control_successes: int,
    control_total: int,
    treatment_successes: int,
    treatment_total: int,
    guardrail_control_events: int,
    guardrail_control_total: int,
    guardrail_treatment_events: int,
    guardrail_treatment_total: int,
    guardrail_margin: float,
    confidence: float = 0.95,
) -> ExperimentResult:
    """Analyze a primary success metric and a lower-is-better guardrail metric."""

    if guardrail_margin < 0.0:
        raise ValueError("Guardrail margin must be non-negative.")

    effect, low, high = _difference_interval(
        control_successes,
        control_total,
        treatment_successes,
        treatment_total,
        confidence,
    )
    guardrail_effect, _, guardrail_high = _difference_interval(
        guardrail_control_events,
        guardrail_control_total,
        guardrail_treatment_events,
        guardrail_treatment_total,
        confidence,
    )

    return ExperimentResult(
        control_rate=control_successes / control_total,
        treatment_rate=treatment_successes / treatment_total,
        absolute_effect=effect,
        confidence_low=low,
        confidence_high=high,
        guardrail_control_rate=guardrail_control_events / guardrail_control_total,
        guardrail_treatment_rate=guardrail_treatment_events / guardrail_treatment_total,
        guardrail_effect=guardrail_effect,
        guardrail_non_inferior=guardrail_high <= guardrail_margin,
    )
