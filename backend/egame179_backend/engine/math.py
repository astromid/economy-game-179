import math
from datetime import datetime

import numpy as np

BULLETIN_SIGMA = 0.3
STOCKS_SIGMA = 0.15


def production_cost(theta: float, price: float, quantity: int) -> float:  # noqa: D103
    return (1 - theta) * price * quantity


def buy_price_next(n_mt: int, n_mt1: int, coeff_h: int, p_mt: float) -> float:  # noqa: D103
    delta_mt = n_mt - n_mt1
    sigma = _sigmoid(delta_mt / coeff_h - math.log(2))
    return round((1.5 * sigma + 0.5) * p_mt, 2)


def sell_price_next(n_mt: int, d_mt: int, coeff_l: int, s_mt: float) -> float:  # noqa: D103
    sigma = _sigmoid((1 - n_mt / d_mt) / coeff_l - math.log(2))
    return round((1.5 * sigma + 0.5) * s_mt, 2)


def theta_next(n_mean: float, coeff_k: int) -> float:  # noqa: D103
    return 0 if n_mean == 0 else round(_sigmoid(2 * n_mean / coeff_k - 3) / 3, 3)


def _sigmoid(x: float) -> float:  # noqa: WPS111
    return 1 / (1 + math.exp(-x))


def delivered_items(ts_start: datetime, ts_finish: datetime, velocity: float, quantity: int) -> int:  # noqa: D103
    delivery_time = (ts_finish - ts_start).total_seconds()
    max_items = math.floor(velocity * delivery_time)
    return min(quantity, max_items)


def sold_items(delivered: int, demand: int, total: int) -> int:  # noqa: D103
    rel_amount = min(1, demand / total)
    return math.floor(rel_amount * delivered)


def bulletin_quantity(quantity: int) -> int:  # noqa: D103
    noised_quantity = math.floor(quantity * (1 + np.random.normal(scale=BULLETIN_SIGMA)))
    return max(1, noised_quantity)


def stocks_price(prev_price: float, rel_income: float) -> float:  # noqa: D103
    noised_coeff = rel_income * (1 + np.random.normal(scale=STOCKS_SIGMA))
    return round(prev_price * max(0.1, noised_coeff), 2)
