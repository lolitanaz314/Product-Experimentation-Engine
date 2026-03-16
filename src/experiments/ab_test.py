import pandas as pd
from scipy.stats import ttest_ind


def evaluate_ab_test(df):

    control = df[df["treatment"] == 0]["conversion"]
    treatment = df[df["treatment"] == 1]["conversion"]

    lift = treatment.mean() - control.mean()

    stat, p_value = ttest_ind(treatment, control)

    return {
        "control_rate": control.mean(),
        "treatment_rate": treatment.mean(),
        "lift": lift,
        "p_value": p_value
    }
