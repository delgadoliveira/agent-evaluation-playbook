# Agent Evaluation Playbook

[![tests](https://github.com/delgadoliveira/agent-evaluation-playbook/actions/workflows/tests.yml/badge.svg)](https://github.com/delgadoliveira/agent-evaluation-playbook/actions/workflows/tests.yml)

A small, vendor-neutral reference implementation for evaluating agentic features across three
evidence layers:

1. **Offline evaluation** — task completion, tool use, required facts, and safety constraints.
2. **Online experimentation** — treatment effects, confidence intervals, and guardrail checks.
3. **Progressive rollout** — evidence-based expand, continue, or hold recommendations by ring.

Everything in this repository uses synthetic tasks and synthetic measurements. It demonstrates
general evaluation methods without including proprietary prompts, product data, internal metrics,
thresholds, tools, dashboards, or unreleased feature details.

## Why this project exists

Agentic systems are hard to evaluate with one score. Their behavior depends on the request,
context, tools, retrieval, model decisions, and the path taken through a task. A practical
evaluation program needs different evidence for different questions:

| Layer | Main question | Example evidence |
|---|---|---|
| Offline | Can the agent perform the task correctly? | Tool calls, rubric coverage, safety checks |
| Online | Does the feature improve user outcomes? | A/B experiment estimates and guardrails |
| Rollout | Does quality remain stable as exposure grows? | Ring-level confidence bounds and failures |

This repository is intentionally small enough to read in one sitting and structured enough to
extend into a real evaluation pipeline.

## Quick start

Requires Python 3.11+ and has no runtime dependencies. Nothing to install, no virtual
environment required, no network access used.

```powershell
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

### What you should see

The test command ends with:

```text
Ran 8 tests in 0.002s

OK
```

The demo prints the path of the report it wrote and nothing else:

```text
artifacts/evaluation-report.md
```

That file is regenerated on every run and is safe to delete. If both commands behave as above,
the repository is working as intended.

Tests and the demo run on Python 3.11, 3.12, and 3.13 in CI on every push, so the commands above
are verified on a clean machine rather than only on mine.

## Repository structure

```text
src/agent_eval_playbook/
  offline.py       # Synthetic agent-task evaluation
  experiments.py   # Difference-in-proportions and guardrails
  rollout.py       # Progressive ring assessment
scripts/
  run_demo.py      # End-to-end example
examples/
  cases.jsonl
  predictions.jsonl
  experiment.csv
  rings.csv
tests/
docs/
  methodology.md
```

## Offline evaluation

Each synthetic case defines:

- expected tools;
- facts that must appear in the response;
- phrases that must not appear;
- a task identifier used for slice-level diagnosis.

Predictions are evaluated deterministically. This keeps the example reproducible and makes the
evaluation contract explicit. In a production setting, semantic criteria can be added with human
labels or calibrated model-based judges.

```python
from agent_eval_playbook.offline import evaluate_case

result = evaluate_case(case, prediction)
print(result.passed, result.required_fact_recall)
```

## Online experimentation

The experiment module reports:

- outcome rates for control and treatment;
- absolute treatment effect;
- a two-sided confidence interval;
- guardrail non-inferiority against a configured margin.

The calculations use standard normal approximations and are intended for education and prototypes,
not as a replacement for an organization's experimentation platform.

## Progressive rollout

Each rollout ring is assessed using:

- minimum sample requirements;
- a Wilson lower confidence bound for task success;
- critical failure counts;
- an explicit expand, continue, or hold recommendation.

The included thresholds are illustrative. Real thresholds must be chosen from the product's risk,
measurement quality, and decision context.

## Safe public-work boundary

This project deliberately avoids:

- internal code names, feature names, and tool names;
- production prompts or system instructions;
- user or enterprise data;
- proprietary evaluation sets;
- internal metric definitions, thresholds, sample sizes, or results;
- screenshots or exports from private dashboards;
- implementation details from an employer's codebase.

The reusable contribution is the **reasoning structure**: define the uncertainty, choose the
evidence that can reduce it, and preserve the decision contract.

## Author

Alan Delgado de Oliveira — Senior Applied Scientist, AI evaluation and experimentation.

The views and code in this repository are personal and do not represent Microsoft.

## License

MIT
