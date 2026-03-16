import numpy as np
import pandas as pd

def simulate_experiment(n_users=10000, uplift=0.05):

    np.random.seed(42)

    users = np.arange(n_users)

    treatment = np.random.binomial(1, 0.5, n_users)

    baseline_conversion = 0.10

    conversion_prob = baseline_conversion + treatment * uplift

    conversions = np.random.binomial(1, conversion_prob)

    df = pd.DataFrame({
        "user_id": users,
        "treatment": treatment,
        "conversion": conversions
    })

    return df


if __name__ == "__main__":
    df = simulate_experiment()
    df.to_csv("data/simulated_experiment.csv", index=False)
