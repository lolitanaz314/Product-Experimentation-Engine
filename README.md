# Product Experimentation Engine

A product data science portfolio project that simulates A/B testing end-to-end, including experiment planning, SRM checks, sequential testing, guardrail monitoring, segmentation analysis, and launch recommendations.

## Why this project exists

Most beginner experimentation projects stop at:
- simulate data
- run a t-test
- print a p-value

This project goes further and models a more realistic product experimentation workflow:
- experiment design and runtime planning
- sample ratio mismatch (SRM) validation
- primary metric evaluation
- guardrail monitoring
- heterogeneous treatment effect analysis
- sequential testing
- launch decisioning

## Business Problem

A product team wants to test a new homepage CTA designed to increase user conversion.

However, increasing conversion should not harm overall user experience.

The experiment evaluates whether the new CTA improves conversion while protecting key guardrail metrics.

---

## Experiment Design

Unit of randomization: user_id

Treatment:
New homepage CTA

Control:
Existing CTA

Primary metric:
Conversion rate

Guardrail metrics:
Bounce rate
Session length

Target MDE:
+2% conversion lift

Statistical settings:
alpha = 0.05
power = 0.8

## Features

- **Synthetic experiment simulation**
  - user-level randomization
  - heterogeneous treatment effects
  - segment columns like platform, user_type, and country
  - guardrail metrics such as bounce and session length

- **Experiment planning**
  - configurable alpha, power, MDE, baseline, daily traffic
  - estimated sample size per group
  - estimated runtime in days

- **A/B test analysis**
  - control vs treatment conversion comparison
  - lift estimation
  - p-value reporting

- **Sequential testing**
  - simple Bonferroni-adjusted repeated-look logic
  - avoids naive peeking at fixed alpha

- **SRM check**
  - validates randomization integrity
  - flags suspicious treatment/control imbalances

- **Guardrail monitoring**
  - detects regressions in secondary product health metrics

- **Segmentation**
  - evaluates treatment lift by platform, user type, and country
  - surfaces cases where average lift hides segment harm

- **Decision engine**
  - recommends `ship`, `hold`, `iterate`, `extend_test`, or `partial_rollout`

- **Interactive dashboard**
  - built with Streamlit

## Repo structure

```text
Product-Experimentation-Engine/
├── configs/
│   └── experiment_config.yaml
├── dashboards/
│   └── app.py
├── data/
│   └── simulated_experiment.csv
├── notebooks/
├── simulations/
│   └── generate_data.py
├── src/
│   ├── analysis/
│   │   ├── guardrails.py
│   │   ├── segmentation.py
│   │   └── srm_check.py
│   ├── decisioning/
│   │   └── decision_engine.py
│   ├── design/
│   │   └── experiment_design.py
│   ├── experiments/
│   │   └── ab_test.py
│   └── stats/
│       ├── power_analysis.py
│       └── sequential_testing.py
├── tests/
├── requirements.txt
└── README.md
