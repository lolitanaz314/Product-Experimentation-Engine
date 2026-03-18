import math
import yaml

def plan_experiment(config_path="configs/experiment_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    baseline = config["expected_baseline"]
    mde = config["mde"]
    daily_traffic = config["daily_traffic"]
    treatment_allocation = config["allocation"]["treatment"]

    # simple fallback (no statsmodels dependency issues)
    sample_size_per_group = int(1000 * (mde / max(baseline, 0.01)))

    runtime_days = math.ceil(
        sample_size_per_group / (daily_traffic * treatment_allocation)
    )

    return {
        "experiment_name": config["experiment_name"],
        "primary_metric": config["primary_metric"],
        "sample_size_per_group": sample_size_per_group,
        "estimated_runtime_days": runtime_days,
        "alpha": config["alpha"],
        "power": config["power"],
        "mde": mde
    }
