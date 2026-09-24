# Methodology notes

## Evaluation is a decision system

The purpose of evaluation is not to maximize a dashboard. It is to reduce uncertainty enough to
make the next product decision responsibly.

The playbook separates three evidence layers because they answer different questions:

- **Offline:** capability, diagnosis, repeatability, and fast iteration.
- **Online:** user-visible impact under realistic operating conditions.
- **Progressive rollout:** stability, rare failures, and changing population exposure.

Disagreement between layers should trigger investigation rather than metric shopping.

## Offline contracts

The example uses deterministic checks so the expected behavior is auditable. A richer system may
combine:

- deterministic assertions;
- reference-based semantic similarity;
- human labels;
- calibrated model-based judges;
- task-specific simulators;
- trajectory and tool-use inspection.

Model-based judges should be treated as measurement instruments. They need calibration, slice
analysis, drift monitoring, and an abstention path.

## Experiment estimates

The example reports an absolute difference in binary rates with a normal-approximation confidence
interval. Production experimentation may require variance reduction, sequential testing, clustered
randomization, multiple-testing controls, or other methods appropriate to the design.

Guardrails are represented as lower-is-better events with a non-inferiority margin. The margin must
be set before looking at the result and should reflect real product risk.

## Rollout recommendations

The ring assessment is intentionally transparent:

1. critical failures cause a hold;
2. insufficient exposure causes continued observation;
3. sufficient evidence above the target supports expansion;
4. ambiguous evidence supports continued observation rather than forced certainty.

This is a teaching example, not a universal ship policy.

## Confidentiality boundary

Public examples should use synthetic tasks, generic tool names, illustrative thresholds, and
standard methods. The value of a public artifact comes from the clarity of the reasoning—not from
reproducing private product details.
