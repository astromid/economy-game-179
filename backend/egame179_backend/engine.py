import math
from collections import defaultdict

from fastapi import HTTPException
import pandas as pd

from egame179_backend.db import (
    BalanceDAO,
    CycleParamsDAO,
    MarketDAO,
    PriceDAO,
    ProductDAO,
    SupplyDAO,
    TransactionDAO,
    UnlockedMarketDAO,
)
from egame179_backend.db.cycle import Cycle
from egame179_backend.db.cycle_params import CycleParams

STOCK_SIGMA = 0.05


async def make_transaction(
    cycle: int,
    user_id: int,
    amount: float,
    description: str,
    items: int | None,
    market_id: int | None,
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
    await transaction_dao.create(
        cycle=cycle,
        user_id=user_id,
        amount=amount,
        description=description,
        items=items,
        market_id=market_id,
    )
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
        items=None,
        market_id=None,
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


async def finish_cycle(
    cycle: Cycle,
    supply_dao: SupplyDAO,
    market_dao: MarketDAO,
    cycle_params_dao: CycleParamsDAO,
    price_dao: PriceDAO,
    balance_dao: BalanceDAO,
    transaction_dao: TransactionDAO,
    product_dao: ProductDAO,
) -> None:
    if cycle.ts_finish is None:
        raise ValueError("Cycle is not finished yet")

    markets = await market_dao.get_all()
    cycle_params = await cycle_params_dao.get(cycle.cycle)
    velocities = get_velocities(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=cycle_params,
    )
    demands = get_demands(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=cycle_params,
    )
    await supply_dao.finish_ongoing(ts_finish=cycle.ts_finish, velocities=velocities)
    # make sell (income) transactions
    supplies = await supply_dao.get(cycle=cycle.cycle)
    prices = await price_dao.get_all(cycle=cycle.cycle)
    sell_prices = {price.market_id: price.sell for price in prices}
    total_supply: dict[int, int] = defaultdict(int)
    for supply in supplies:
        total_supply[supply.market_id] += supply.amount

    for supply in supplies:
        sell_price = sell_prices[supply.market_id]
        rel_amount = min(1, demands[supply.market_id] / total_supply[supply.market_id])
        real_amount = math.floor(rel_amount * supply.amount)
        await make_transaction(
            cycle=cycle.cycle,
            user_id=supply.user_id,
            amount=real_amount * sell_price,
            description=f"Sell {real_amount} items (market {supply.market_id}, price {sell_price})",
            items=supply.amount,  # !Use amount without demand correction for further price calculation
            market_id=supply.market_id,
            overdraft=False,
            inflow=True,
            balance_dao=balance_dao,
            transaction_dao=transaction_dao,
        )
        if real_amount < supply.declared_amount:
            product = await product_dao.get(cycle=cycle.cycle, user_id=supply.user_id, market_id=supply.market_id)
            product.storage += supply.declared_amount - real_amount
            await product_dao.add(product)
            supply.amount = real_amount
            await supply_dao.add(supply)
    # make per-user fees
    products = await product_dao.get_all(cycle=cycle.cycle)
    storage: dict[int, int] = defaultdict(int)
    for product in products:
        storage[product.user_id] += product.storage
    for user_id, user_storage in storage.items():
        if user_storage > 0:
            await make_transaction(
                cycle=cycle.cycle,
                user_id=user_id,
                amount=user_storage * cycle_params.gamma,
                description=f"Storage fee ({user_storage} total items, {cycle_params.gamma}/item)",
                items=None,
                market_id=None,
                overdraft=True,
                inflow=False,
                balance_dao=balance_dao,
                transaction_dao=transaction_dao,
            )
        await make_transaction(
            cycle=cycle.cycle,
            user_id=user_id,
            amount=cycle_params.alpha,
            description="Life fee",
            items=None,
            market_id=None,
            overdraft=True,
            inflow=False,
            balance_dao=balance_dao,
            transaction_dao=transaction_dao,
        )
    overdrafted_balances = await balance_dao.get_overdrafted(cycle=cycle.cycle)
    for balance in overdrafted_balances:
        await make_transaction(
            cycle=cycle.cycle,
            user_id=balance.user_id,
            amount=abs(balance.amount) * cycle_params.overdraft_rate,
            description="Fee for overdraft",
            items=None,
            market_id=None,
            overdraft=True,
            inflow=False,
            balance_dao=balance_dao,
            transaction_dao=transaction_dao,
        )


async def create_cycle(
    cycle: int,  # new cycle, finished = -1, prev = -2
    cycle_params_dao: CycleParamsDAO,
    price_dao: PriceDAO,
    transaction_dao: TransactionDAO,
    market_dao: MarketDAO,
) -> None:
    markets = await market_dao.get_all()
    cycle_params = await cycle_params_dao.get(cycle - 1)
    # 1. Calculate new prices
    prices = await price_dao.get_all(cycle=cycle - 1)
    market2price = {price.market_id: price for price in prices}
    transactions = await transaction_dao.get(user_id=None)
    demands = get_demands(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=cycle_params,
    )
    # take prev & prev-prev transactions
    transactions_df = pd.DataFrame([tr.dict() for tr in transactions if tr.cycle >= cycle - 2])
    transactions_df = transactions_df.dropna(subset=["market_id", "items"])

    buy_df = transactions_df[transactions_df["amount"] < 0]
    sell_df = transactions_df[transactions_df["amount"] > 0]

    buy_market = buy_df[buy_df["cycle"] == cycle - 1].groupby("market_id")["items"].sum().to_dict()
    buy_market_prev = buy_df[buy_df["cycle"] == cycle - 2].groupby("market_id")["items"].sum().to_dict()
    sell_market = sell_df[sell_df["cycle"] == cycle - 1].groupby("market_id")["items"].sum().to_dict()

    for market in markets:
        price = market2price[market.id]
        new_buy_price = buy_price_next(
            n_mt=buy_market.get(market.id, 0),
            n_mt1=buy_market_prev.get(market.id, 0),
            h=cycle_params.coeff_h,
            p_mt=price.buy,
        )
        new_sell_price = sell_price_next(
            n_mt=sell_market.get(market.id, 0),
            d_mt=demands[market.id],
            l=cycle_params.coeff_l,
            s_mt=price.sell,
        )
        await price_dao.create(
            cycle=cycle,
            market_id=market.id,
            buy=new_buy_price,
            sell=new_sell_price,
        )


def get_velocities(m_id2ring: dict[int, int], cycle_params: CycleParams) -> dict[int, float]:
    ring2demand = {
        0: cycle_params.demand_ring0,
        1: cycle_params.demand_ring1,
        2: cycle_params.demand_ring2,
    }
    return {m_id: ring2demand[m_id2ring[m_id]] / cycle_params.tau_s for m_id in m_id2ring}


def get_demands(m_id2ring: dict[int, int], cycle_params: CycleParams) -> dict[int, int]:
    ring2demand = {
        0: cycle_params.demand_ring0,
        1: cycle_params.demand_ring1,
        2: cycle_params.demand_ring2,
    }
    return {m_id: ring2demand[m_id2ring[m_id]] for m_id in m_id2ring}


def buy_price_next(n_mt: int, n_mt1: int, h: int, p_mt: float) -> float:  # noqa: WPS111
    delta_mt = n_mt - n_mt1
    sigma = _sigmoid(delta_mt / h - math.log(2))
    coef = 1.5 * sigma + 0.5  # noqa: WPS432
    return coef * p_mt


def sell_price_next(n_mt: int, d_mt: int, l: int, s_mt: float) -> float:  # noqa: WPS111, E741
    sigma = _sigmoid((1 - n_mt / d_mt) / l - math.log(2))
    coef = 1.5 * sigma + 0.5  # noqa: WPS432
    return coef * s_mt


def theta_next(n_imt: list[int], k: int) -> float:  # noqa: WPS111
    n_mean = sum(n_imt) / len(n_imt)
    return _sigmoid(2 * n_mean / k - 3) / 3


def _sigmoid(x: float) -> float:  # noqa: WPS111
    return 1 / (1 + math.exp(-x))
