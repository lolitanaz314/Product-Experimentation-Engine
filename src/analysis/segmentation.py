import pandas as pd


def segment_lift(df, segment_col):
    """
    Computes conversion rates and lift within each segment.
    """

    rows = []

    for segment_value in df[segment_col].dropna().unique():
        seg_df = df[df[segment_col] == segment_value]

        control = seg_df[seg_df["treatment"] == 0]["conversion"]
        treatment = seg_df[seg_df["treatment"] == 1]["conversion"]

        if len(control) == 0 or len(treatment) == 0:
            continue

        control_rate = control.mean()
        treatment_rate = treatment.mean()
        lift = treatment_rate - control_rate

        rows.append({
            "segment": segment_col,
            "segment_value": segment_value,
            "n_users": len(seg_df),
            "control_rate": control_rate,
            "treatment_rate": treatment_rate,
            "lift": lift
        })

    return pd.DataFrame(rows).sort_values("lift", ascending=False)
