import numpy as np


def cuped_adjustment(y, x):

    theta = np.cov(y, x)[0,1] / np.var(x)

    y_cuped = y - theta * (x - np.mean(x))

    return y_cuped
