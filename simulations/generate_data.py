import numpy as np
import pandas as pd


def simulate_experiment(
    n_users=10000,
    uplift=0.03,
    seed=42,
    mobile_share=0.7,
    new_user_share=0.4,
    us_share=0.6,
    induce_srm=False,
    mobile_guardrail_hit=True,
    heterogeneous_effects=True,
):
    np.random.seed(seed)

    users = np.arange(n_users)

    # Assignment
    if induce_srm:
        treatment = np.random.binomial(1, 0.54, n_users)
    else:
        treatment = np.random.binomial(1, 0.50, n_users)

    platform = np.random.choice(
        ["mobile", "desktop"],
        size=n_users,
        p=[mobile_share, 1 - mobile_share],
    )

    user_type = np.random.choice(
        ["new", "returning"],
        size=n_users,
        p=[new_user_share, 1 - new_user_share],
    )

    country = np.random.choice(
        ["US", "INTL"],
        size=n_users,
        p=[us_share, 1 - us_share],
    )

    # Baseline conversion
    baseline_conversion = np.where(user_type == "returning", 0.14, 0.07)

    # Heterogeneous treatment effect
    if heterogeneous_effects:
        platform_uplift = np.where(platform == "desktop", uplift, uplift - 0.015)
        user_uplift = np.where(user_type == "new", 0.015, 0.0)
        total_uplift = platform_uplift + user_uplift
    else:
        total_uplift = uplift

    final_prob = baseline_conversion + (treatment * total_uplift)
    final_prob = np.clip(final_prob, 0, 1)
    conversion = np.random.binomial(1, final_prob)

    # Guardrail 1: bounce
    baseline_bounce = np.where(platform == "mobile", 0.38, 0.28)

    if mobile_guardrail_hit:
        bounce_penalty = np.where((treatment == 1) & (platform == "mobile"), 0.03, 0.0)
    else:
        bounce_penalty = 0.0

    bounce_prob = np.clip(baseline_bounce + bounce_penalty, 0, 1)
    bounced = np.random.binomial(1, bounce_prob)

    # Guardrail 2: session length
    baseline_session = np.where(user_type == "returning", 8.0, 5.5)

    if mobile_guardrail_hit:
        session_shift = np.where((treatment == 1) & (platform == "mobile"), -0.7, 0.2)
    else:
        session_shift = np.where(treatment == 1, 0.2, 0.0)

    session_length = np.maximum(
        np.random.normal(
            loc=baseline_session + session_shift,
            scale=1.5,
            size=n_users,
        ),
        0.5,
    )

    df = pd.DataFrame(
        {
            "user_id": users,
            "treatment": treatment,
            "platform": platform,
            "user_type": user_type,
            "country": country,
            "conversion": conversion,
            "bounced": bounced,
            "session_length": session_length,
        }
    )

    return df