"""Progressive rollout assessments for synthetic ring-level observations."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist


@dataclass(frozen=True)
class RingAssessment:
    ring: str
    observed_rate: float
    lower_confidence_bound: float
    critical_failures: int
    recommendation: str
    reason: str


def wilson_lower_bound(successes: int, total: int, confidence: float = 0.95) -> float:
    """Return the lower Wilson score bound for a binomial proportion."""

    if total <= 0:
        raise ValueError("Total must be positive.")
    if successes < 0 or successes > total:
        raise ValueError("Successes must be between zero and total.")
    if not 0.0 < confidence < 1.0:
        raise ValueError("Confidence must be between zero and one.")

    proportion = successes / total
    z_value = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    denominator = 1.0 + z_value**2 / total
    center = proportion + z_value**2 / (2.0 * total)
    adjustment = z_value * sqrt(
        proportion * (1.0 - proportion) / total + z_value**2 / (4.0 * total**2)
    )
    return (center - adjustment) / denominator


def assess_ring(
    *,
    ring: str,
    successes: int,
    total: int,
    critical_failures: int,
    target_rate: float,
    minimum_samples: int,
    confidence: float = 0.95,
) -> RingAssessment:
    """Return an illustrative rollout recommendation with an explicit reason."""

    if critical_failures < 0:
        raise ValueError("Critical failures must be non-negative.")
    if not 0.0 <= target_rate <= 1.0:
        raise ValueError("Target rate must be between zero and one.")
    if minimum_samples <= 0:
        raise ValueError("Minimum samples must be positive.")

    observed_rate = successes / total
    lower_bound = wilson_lower_bound(successes, total, confidence)

    if critical_failures:
        recommendation = "hold"
        reason = "At least one critical failure requires investigation before expansion."
    elif total < minimum_samples:
        recommendation = "continue"
        reason = "The ring has not reached the illustrative minimum sample requirement."
    elif lower_bound >= target_rate:
        recommendation = "expand"
        reason = "The lower confidence bound meets the illustrative target with no critical failures."
    else:
        recommendation = "continue"
        reason = "Evidence is not yet strong enough to support expansion."

    return RingAssessment(
        ring=ring,
        observed_rate=observed_rate,
        lower_confidence_bound=lower_bound,
        critical_failures=critical_failures,
        recommendation=recommendation,
        reason=reason,
    )
