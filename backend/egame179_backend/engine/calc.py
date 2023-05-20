from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
from icecream import ic

from egame179_backend.db.cycle import Cycle
from egame179_backend.db.market import MarketShare
from egame179_backend.db.market_price import MarketPrice
from egame179_backend.db.stocks import Stock
from egame179_backend.db.supply import Supply
from egame179_backend.db.theta import Theta
from egame179_backend.engine.math import buy_price_next, delivered_items, sell_price_next, stocks_price, theta_next


def calculate_delivered(
    supplies: list[Supply],
    ts_finish: datetime,
    velocities: dict[int, float],
) -> tuple[list[Supply], dict[int, int]]:
    """Calculate delivered items for all supplies.

    Args:
        supplies (list[Supply]): list of supplies.
        ts_finish (datetime): cycle finish time.
        velocities (dict[int, float]): {market: velocity}.

    Returns:
        tuple[list[Supply], dict[int, int]]: (updated supplies, total delivered).
    """
    total_delivered: dict[int, int] = defaultdict(int)
    for supply in supplies:
        supply.ts_finish = ts_finish
        supply.delivered = delivered_items(
            ts_start=supply.ts_start,
            ts_finish=ts_finish,
            velocity=velocities[supply.market],
            quantity=supply.quantity,
        )
        total_delivered[supply.market] += supply.delivered
    return supplies, total_delivered


def calculate_shares(
    shares: list[MarketShare],
    sold_per_market: dict[int, int],
    sold_per_user_market: dict[tuple[int, int], int],
    previous_owners: dict[tuple[int, int], int],
) -> dict[int, list[MarketShare]]:
    """Calculate shares for all markets.

    Args:
        shares (list[MarketShare]): list of shares.
        sold_per_market (dict[int, int]): total sold items per market.
        sold_per_user_market (dict[tuple[int, int], int]): total sold items per user per market.
        previous_owners (dict[tuple[int, int], int]): previous owners for all markets.

    Returns:
        dict[int, list[MarketShare]]: {market: list of shares}.
    """
    market_shares: dict[int, list[MarketShare]] = defaultdict(list)
    for share in shares:
        total_market = sold_per_market.get(share.market, 0)
        if total_market == 0:
            if share.user == previous_owners.get((share.market, 1), -1):
                # prev owner is still top1
                share.share = 1.02
            elif share.user == previous_owners.get((share.market, 2), -1):
                # prev owner is still top2
                share.share = 1.01
        else:
            share.share = sold_per_user_market.get((share.user, share.market), 0) / total_market
        if share.share > 0:
            market_shares[share.market].append(share)
    return market_shares


def calculate_new_prices(
    cycle: Cycle,
    prices: list[MarketPrice],
    prod_df: pd.DataFrame,
    supp_df: pd.DataFrame,
    demand: dict[int, int],
) -> dict[int, tuple[float, float]]:
    """Calculate new prices for all markets.

    Args:
        cycle (Cycle): finished cycle.
        prices (list[MarketPrice]): previous prices.
        prod_df (pd.DataFrame): production dataframe.
        supp_df (pd.DataFrame): supplies dataframe.
        demand (dict[int, int]): demand for all markets.

    Returns:
        dict[int, tuple[float, float]]: new prices.
    """
    if prod_df.empty:
        market_production = {}
    else:
        market_production = prod_df.groupby(["cycle", "market"])["quantity"].sum().to_dict()

    if supp_df.empty:
        market_delivered = {}
    else:
        market_delivered = supp_df.groupby("market")["delivered"].sum().to_dict()

    new_prices: dict[int, tuple[float, float]] = {}
    for price in prices:
        buy_price = buy_price_next(
            n_mt=market_production.get((cycle.id, price.market), 0),
            n_mt1=market_production.get((cycle.id - 1, price.market), 0),
            coeff_h=cycle.coeff_h,
            p_mt=price.buy,
        )
        sell_price = sell_price_next(
            n_mt=market_delivered.get(price.market, 0),
            d_mt=demand[price.market],
            coeff_l=cycle.coeff_l,
            s_mt=price.sell,
        )
        new_prices[price.market] = (buy_price, sell_price)
    return new_prices


def calculate_new_thetas(cycle: Cycle, thetas: list[Theta], prod_df: pd.DataFrame) -> dict[tuple[int, int], float]:
    """Calculate new thetas for all users.

    Args:
        cycle (Cycle): finished cycle.
        thetas (list[Theta]): list of previous thetas.
        prod_df (pd.DataFrame): production dataframe.

    Returns:
        dict[tuple[int, int], float]: _description_
    """
    if prod_df.empty:
        user_mean_production = {}
    else:
        user_production = prod_df.groupby(["user", "market", "cycle"])["quantity"].sum().reset_index()
        user_mean_production = user_production.groupby(["user", "market"])["quantity"].mean().to_dict()

    new_thetas: dict[tuple[int, int], float] = {}
    for theta in thetas:
        new_thetas[(theta.user, theta.market)] = theta_next(
            n_mean=user_mean_production.get((theta.user, theta.market), 0),
            coeff_k=cycle.coeff_k,
        )
    return new_thetas


def calculate_new_stocks(
    cycle: int,
    stocks: list[Stock],
    balances_df: pd.DataFrame,
    storages_df: pd.DataFrame,
    npc_df: pd.DataFrame,
    initial_balance: float,
) -> dict[int, float]:
    """Calculate new stocks for all users.

    Args:
        cycle (int): finished cycle.
        stocks (list[Stock]): list of previous stocks.
        balances_df (pd.DataFrame): balances dataframe.
        storages_df (pd.DataFrame): storage dataframe.
        npc_df (pd.DataFrame): npc dataframe.
        initial_balance (float): initial balance.

    Returns:
        dict[int, float]: {user: new stock}.
    """
    # player stocks
    if balances_df.empty:
        rel_incomes = {}
    else:
        balances_df = balances_df.sort_values(["user", "cycle"])
        balances_df["prev_balance"] = balances_df.groupby("user")["balance"].shift(1).fillna(initial_balance)
        # avoid division by zero
        balances_df["prev_balance"] = balances_df["prev_balance"].replace(0, np.nan).fillna(1)
        balances_df = balances_df[balances_df["cycle"] == cycle]
        balances_df["rel_income"] = balances_df["balance"] / balances_df["prev_balance"]
        balances_df = balances_df.set_index("user")
        ic(balances_df)
        rel_incomes = balances_df["rel_income"].to_dict()
    # NPC stocks
    if storages_df.empty:
        rel_storages = {}
    else:
        storages_df = storages_df.merge(npc_df, on="market", how="left")
        storages_df = storages_df.groupby(["npc", "cycle"])["quantity"].sum().reset_index()
        storages_df = storages_df.sort_values(["npc", "cycle"])
        storages_df["prev_quantity"] = storages_df.groupby("npc")["quantity"].shift(1).fillna(10)
        # avoid division by zero
        storages_df["prev_quantity"] = storages_df["prev_quantity"].replace(0, 1)
        storages_df = storages_df[storages_df["cycle"] == cycle]
        storages_df["rel_income"] = storages_df["quantity"] / storages_df["prev_quantity"]
        storages_df = storages_df.set_index("npc")
        ic(storages_df)
        rel_storages = storages_df["rel_income"].to_dict()
    ic(rel_incomes)
    ic(rel_storages)
    new_stocks: dict[int, float] = {}
    for stock in stocks:
        rel_income = rel_incomes.get(stock.user, rel_storages.get(stock.user, 1))
        new_stocks[stock.user] = stocks_price(prev_price=stock.price, rel_income=rel_income)
    return new_stocks
