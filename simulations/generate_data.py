import numpy as np
import pandas as pd


def simulate_experiment(n_users=10000, uplift=0.03):
    np.random.seed(42)

    users = np.arange(n_users)
    treatment = np.random.binomial(1, 0.5, n_users)

    platform = np.random.choice(["mobile", "desktop"], size=n_users, p=[0.7, 0.3])
    user_type = np.random.choice(["new", "returning"], size=n_users, p=[0.4, 0.6])
    country = np.random.choice(["US", "INTL"], size=n_users, p=[0.6, 0.4])

    baseline_conversion = np.where(user_type == "returning", 0.14, 0.07)

    # heterogeneous treatment effects
    platform_uplift = np.where(platform == "desktop", uplift, uplift - 0.015)
    user_uplift = np.where(user_type == "new", 0.015, 0.0)

    final_prob = baseline_conversion + (treatment * (platform_uplift + user_uplift))
    final_prob = np.clip(final_prob, 0, 1)

    conversion = np.random.binomial(1, final_prob)

    # guardrails
    baseline_bounce = np.where(platform == "mobile", 0.38, 0.28)
    bounce_penalty = np.where((treatment == 1) & (platform == "mobile"), 0.03, 0.0)
    bounce_rate_prob = np.clip(baseline_bounce + bounce_penalty, 0, 1)
    bounced = np.random.binomial(1, bounce_rate_prob)

    baseline_session = np.where(user_type == "returning", 8.0, 5.5)
    session_penalty = np.where((treatment == 1) & (platform == "mobile"), -0.7, 0.2)
    session_length = np.maximum(
        np.random.normal(loc=baseline_session + session_penalty, scale=1.5, size=n_users),
        0.5
    )

    df = pd.DataFrame({
        "user_id": users,
        "treatment": treatment,
        "platform": platform,
        "user_type": user_type,
        "country": country,
        "conversion": conversion,
        "bounced": bounced,
        "session_length": session_length
    })

    return df


if __name__ == "__main__":
    df = simulate_experiment()
    df.to_csv("data/simulated_experiment.csv", index=False)
    print("saved data/simulated_experiment.csv")
