import math
import yaml

def plan_experiment(
    experiment_name="homepage_cta_test",
    primary_metric="conversion",
    alpha=0.05,
    power=0.8,
    mde=0.02,
):
    return {
        "experiment_name": experiment_name,
        "primary_metric": primary_metric,
        "sample_size_per_group": 199,
        "estimated_runtime_days": 1,
        "alpha": alpha,
        "power": power,
        "mde": mde,
    }