from scipy.stats import chisquare


def check_srm(df, expected_treatment_ratio=0.5):
    """
    Checks Sample Ratio Mismatch (SRM).

    If randomization is healthy and expected is 50/50,
    observed counts should be close to that split.
    """

    observed_treatment = (df["treatment"] == 1).sum()
    observed_control = (df["treatment"] == 0).sum()
    total = len(df)

    expected_treatment = total * expected_treatment_ratio
    expected_control = total * (1 - expected_treatment_ratio)

    stat, p_value = chisquare(
        f_obs=[observed_control, observed_treatment],
        f_exp=[expected_control, expected_treatment]
    )

    return {
        "observed_control": int(observed_control),
        "observed_treatment": int(observed_treatment),
        "expected_control": float(expected_control),
        "expected_treatment": float(expected_treatment),
        "srm_p_value": float(p_value),
        "srm_passed": bool(p_value >= 0.01)
    }
