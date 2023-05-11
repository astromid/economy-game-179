import math

from fastapi import HTTPException

from egame179_backend.db import BalanceDAO, SupplyDAO, TransactionDAO


async def make_transaction(
    cycle: int,
    user_id: int,
    amount: float,
    description: str,
    overdraft: bool,
    inflow: bool,
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
        inflow (bool): inflow or outflow transaction.
        balance_dao (BalanceDAO): balances data access object.
        transaction_dao (TransactionDAO): transactions data access object.

    Raises:
        HTTPException: not enough money to make a transaction.

    Returns:
        bool: transaction success.
    """
    balance = await balance_dao.get(cycle=cycle, user_id=user_id)
    if not inflow:
        if not overdraft and balance.amount < amount:
            raise HTTPException(status_code=400, detail="Not enough money to make a transaction")
        amount = -amount
    balance.amount += amount
    await transaction_dao.create(cycle=cycle, user_id=user_id, amount=amount, description=description)
    await balance_dao.add(balance)
    return True


async def make_supply(
    cycle: int,
    user_id: int,
    market_id: int,
    amount: int,
    storage: int,
    beta: float,
    balance_dao: BalanceDAO,
    transaction_dao: TransactionDAO,
    supply_dao: SupplyDAO,
) -> bool:
    """Start new supply and take operation fee.

    Args:
        cycle (int): supply cycle.
        user_id (int): supply user id.
        market_id (int): supply market id.
        amount (int): declared amount of items.
        storage (int): number of items in storage.
        beta (float): current fee.
        balance_dao (BalanceDAO): balances data access object.
        transaction_dao (TransactionDAO): transactions data access object.
        supply_dao (SupplyDAO): supplies data access object.

    Raises:
        HTTPException: not enough items to start a supply.

    Returns:
        bool: supply start success.
    """
    if storage < amount:
        raise HTTPException(status_code=400, detail="No sufficient items on a storage")
    await make_transaction(
        cycle=cycle,
        user_id=user_id,
        amount=beta,
        description="Fee for market operations",
        inflow=False,
        overdraft=True,
        balance_dao=balance_dao,
        transaction_dao=transaction_dao,
    )
    await supply_dao.create(cycle=cycle, user_id=user_id, market_id=market_id, declared_amount=amount)
    return True


def production_cost(theta: float, price: float, number: int) -> float:
    """Cost of production.

    Args:
        theta (float): player current theta.
        price (float): current market price.
        number (int): amount of items.

    Returns:
        float: production cost.
    """
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
