import math

from fastapi import HTTPException

from egame179_backend.db.balance import BalanceDAO
from egame179_backend.db.transaction import TransactionDAO


async def make_transaction(
    cycle: int,
    user_id: int,
    amount: float,
    description: str,
    overdraft: bool,
    balance_dao: BalanceDAO,
    transaction_dao: TransactionDAO,
) -> bool:
    """Make a transaction and update user balance.

    Args:
        cycle (int): transaction cycle.
        user_id (int): transaction user id.
        amount (float): transaction amount.
        description (str): transaction description.
        overdraft (bool): do not check balance.
        balance_dao (BalanceDAO): balances data access object.
        transaction_dao (TransactionDAO): transactions data access object.

    Raises:
        HTTPException: not enough money to make a transaction.

    Returns:
        bool: transaction success.
    """
    if not overdraft:
        balance = await balance_dao.get_on_cycle(cycle=cycle, user_id=user_id)
        if amount > balance.amount:
            raise HTTPException(status_code=400, detail="Not enough money to make a transaction")
    await transaction_dao.create(cycle=cycle, user_id=user_id, amount=amount, description=description)
    await balance_dao.update(cycle=cycle, user_id=user_id, delta=amount)
    return True


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
