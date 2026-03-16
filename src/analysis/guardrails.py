def evaluate_guardrails(df):
    """
    Evaluates whether guardrail metrics got worse in treatment.

    For bounced: higher is worse
    For session_length: lower is worse
    """

    control = df[df["treatment"] == 0]
    treatment = df[df["treatment"] == 1]

    control_bounce = control["bounced"].mean()
    treatment_bounce = treatment["bounced"].mean()

    control_session = control["session_length"].mean()
    treatment_session = treatment["session_length"].mean()

    results = {
        "bounce_rate": {
            "control": control_bounce,
            "treatment": treatment_bounce,
            "delta": treatment_bounce - control_bounce,
            "status": "worse" if treatment_bounce > control_bounce else "ok"
        },
        "session_length": {
            "control": control_session,
            "treatment": treatment_session,
            "delta": treatment_session - control_session,
            "status": "worse" if treatment_session < control_session else "ok"
        }
    }

    return results
