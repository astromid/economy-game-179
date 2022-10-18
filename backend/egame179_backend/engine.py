import math


def production_cost(theta: float, price: float, number: int) -> float:
    return (1 - theta) * price * number


def sigmoid(x: float) -> float:  # noqa: WPS111
    return 1 / (1 + math.exp(-x))


def theta_next(n_imt: list[int], k: int) -> float:  # noqa: WPS111
    n_mean = sum(n_imt) / len(n_imt)
    return sigmoid(2 * n_mean / k - 3) / 3


def buy_price_next(n_mt: int, n_mt1: int, h: int, p_mt: float) -> float:  # noqa: WPS111
    delta_mt = n_mt - n_mt1
    sigma = sigmoid(delta_mt / h - math.log(2))
    coef = 1.5 * sigma + 0.5  # noqa: WPS432
    return coef * p_mt


def sell_price_next(n_mt: int, d_mt: int, l: int, s_mt: float) -> float:  # noqa: WPS111, E741
    sigma = sigmoid((1 - n_mt / d_mt) / l - math.log(2))
    coef = 1.5 * sigma + 0.5  # noqa: WPS432
    return coef * s_mt
