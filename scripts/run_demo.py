"""Run the synthetic evaluation playbook and write a Markdown report."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_eval_playbook.experiments import analyze_binary_experiment
from agent_eval_playbook.offline import evaluate_suite
from agent_eval_playbook.rollout import assess_ring


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def percentage(value: float) -> str:
    return f"{value:.1%}"


cases = read_jsonl(ROOT / "examples" / "cases.jsonl")
predictions = read_jsonl(ROOT / "examples" / "predictions.jsonl")
offline_results = evaluate_suite(cases, predictions)

experiment_rows = {row["arm"]: row for row in read_csv(ROOT / "examples" / "experiment.csv")}
control = experiment_rows["control"]
treatment = experiment_rows["treatment"]
experiment = analyze_binary_experiment(
    control_successes=int(control["task_successes"]),
    control_total=int(control["total_sessions"]),
    treatment_successes=int(treatment["task_successes"]),
    treatment_total=int(treatment["total_sessions"]),
    guardrail_control_events=int(control["guardrail_events"]),
    guardrail_control_total=int(control["total_sessions"]),
    guardrail_treatment_events=int(treatment["guardrail_events"]),
    guardrail_treatment_total=int(treatment["total_sessions"]),
    guardrail_margin=0.01,
)

ring_assessments = [
    assess_ring(
        ring=row["ring"],
        successes=int(row["successes"]),
        total=int(row["total"]),
        critical_failures=int(row["critical_failures"]),
        target_rate=float(row["target_rate"]),
        minimum_samples=int(row["minimum_samples"]),
    )
    for row in read_csv(ROOT / "examples" / "rings.csv")
]

passed = sum(result.passed for result in offline_results)
report = [
    "# Synthetic Agent Evaluation Report",
    "",
    "> All tasks and measurements in this report are synthetic.",
    "",
    "## 1. Offline evaluation",
    "",
    f"Suite pass rate: **{passed}/{len(offline_results)} ({passed / len(offline_results):.1%})**",
    "",
    "| Case | Task | Pass | Tool recall | Fact recall | Diagnosis |",
    "|---|---|---:|---:|---:|---|",
]
for result in offline_results:
    diagnosis_parts = []
    if result.missing_tools:
        diagnosis_parts.append(f"missing tools: {', '.join(result.missing_tools)}")
    if result.missing_facts:
        diagnosis_parts.append(f"missing facts: {', '.join(result.missing_facts)}")
    if result.forbidden_matches:
        diagnosis_parts.append(f"forbidden: {', '.join(result.forbidden_matches)}")
    diagnosis = "; ".join(diagnosis_parts) or "none"
    report.append(
        f"| {result.case_id} | {result.task} | {'yes' if result.passed else 'no'} | "
        f"{percentage(result.tool_recall)} | {percentage(result.required_fact_recall)} | {diagnosis} |"
    )

report.extend(
    [
        "",
        "## 2. Online experiment",
        "",
        f"- Control task success: **{percentage(experiment.control_rate)}**",
        f"- Treatment task success: **{percentage(experiment.treatment_rate)}**",
        f"- Absolute effect: **{percentage(experiment.absolute_effect)}**",
        f"- 95% confidence interval: **[{percentage(experiment.confidence_low)}, "
        f"{percentage(experiment.confidence_high)}]**",
        f"- Guardrail non-inferior within the illustrative margin: "
        f"**{'yes' if experiment.guardrail_non_inferior else 'no'}**",
        "",
        "## 3. Progressive rollout",
        "",
        "| Ring | Observed success | Lower bound | Critical failures | Recommendation | Reason |",
        "|---|---:|---:|---:|---|---|",
    ]
)
for assessment in ring_assessments:
    report.append(
        f"| {assessment.ring} | {percentage(assessment.observed_rate)} | "
        f"{percentage(assessment.lower_confidence_bound)} | {assessment.critical_failures} | "
        f"**{assessment.recommendation}** | {assessment.reason} |"
    )

report.extend(
    [
        "",
        "## Decision note",
        "",
        "The synthetic treatment shows a positive primary effect and an acceptable guardrail result. "
        "The preview ring is still held because a critical failure overrides aggregate quality. "
        "This illustrates why offline, online, and rollout evidence should remain distinct.",
        "",
    ]
)

artifact_dir = ROOT / "artifacts"
artifact_dir.mkdir(exist_ok=True)
output = artifact_dir / "evaluation-report.md"
output.write_text("\n".join(report), encoding="utf-8")
print(output)
