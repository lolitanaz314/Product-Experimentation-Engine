from statsmodels.stats.power import TTestIndPower


def required_sample_size(effect_size, power=0.8, alpha=0.05):

    analysis = TTestIndPower()

    sample_size = analysis.solve_power(
        effect_size=effect_size,
        power=power,
        alpha=alpha
    )

    return int(sample_size)
