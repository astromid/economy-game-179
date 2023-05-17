from collections import defaultdict
from datetime import datetime

import pandas as pd

from egame179_backend.db import BalanceDAO, MarketDAO, WarehouseDAO, WorldDemandDAO
from egame179_backend.db.market import MarketShare
from egame179_backend.db.supply import Supply
from egame179_backend.db.transaction import Transaction
from egame179_backend.engine.math import delivered_items, sold_items


async def check_balance(cycle: int, user: int, amount: float, balance_dao: BalanceDAO) -> bool:
    """Check user balance for transaction.

    Args:
        cycle (int): current cycle.
        user (int): target user id.
        amount (float): transaction amount.
        balance_dao (BalanceDAO): balances table DAO.

    Returns:
        bool: transaction amount <= balance.
    """
    balance = await balance_dao.get(cycle=cycle, user=user)
    return amount <= balance


async def check_storage(cycle: int, user: int, market: int, quantity: int, wh_dao: WarehouseDAO) -> bool:
    """Check user storage for supply.

    Args:
        cycle (int): current cycle.
        user (int): target user id.
        market (int): target market id.
        quantity (int): number of items.
        wh_dao (WarehouseDAO): warehouses table DAO.

    Returns:
        bool: warehouse quantity <= quantity.
    """
    storage = await wh_dao.get(cycle=cycle, user=user, market=market)
    return quantity <= storage


async def get_market_names(market_dao: MarketDAO) -> dict[int, str]:
    """Get market names mapping.

    Args:
        market_dao (MarketDAO): markets table DAO.

    Returns:
        dict[int, str]: {market id: name}.
    """
    markets = await market_dao.select_markets()
    return {market.id: market.name for market in markets}


async def get_market_rings(market_dao: MarketDAO) -> dict[int, int]:
    """Get market rings mapping.

    Args:
        market_dao (MarketDAO): markets table DAO.

    Returns:
        dict[int, int]: {market id: ring}.
    """
    markets = await market_dao.select_markets()
    return {market.id: market.ring for market in markets}


async def get_world_demand(cycle: int, market_dao: MarketDAO, wd_dao: WorldDemandDAO) -> dict[int, int]:
    """Get demand for all markets.

    Args:
        cycle (int): current cycle.
        market_dao (MarketDAO): markets table DAO.
        wd_dao (WorldDemandDAO): world_demand table DAO.

    Returns:
        dict[int, int]: {market: demand}.
    """
    market2ring = await get_market_rings(market_dao)
    demand = await wd_dao.select(cycle=cycle)
    return {market: demand[ring] for market, ring in market2ring.items()}


async def get_supply_velocities(
    cycle: int,
    tau_s: int,
    market_dao: MarketDAO,
    wd_dao: WorldDemandDAO,
) -> dict[int, float]:
    """Get supply velocities for all markets.

    Args:
        cycle (int): current cycle.
        tau_s (int): time of full supply.
        market_dao (MarketDAO): markets table DAO.
        wd_dao (WorldDemandDAO): world_demand table DAO.

    Returns:
        dict[int, float]: {market: velocity}.
    """
    market2ring = await get_market_rings(market_dao)
    demand = await wd_dao.select(cycle=cycle)
    return {market: demand[ring] / tau_s for market, ring in market2ring.items()}


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


def calculate_sold(
    cycle: int,
    supplies: list[Supply],
    demand: dict[int, int],
    total_delivered: dict[int, int],
    sell_prices: dict[int, float],
    market_names: dict[int, str],
) -> tuple[list[Supply], list[Transaction]]:
    """Calculate sold items for all supplies.

    Args:
        cycle (int): target cycle.
        supplies (list[Supply]): list of supplies.
        demand (dict[int, int]): demand for all markets.
        total_delivered (dict[int, int]): total delivered items for all markets.
        sell_prices (dict[int, float]): sell prices for all markets.
        market_names (dict[int, str]): market names mapping.

    Returns:
        tuple[list[Supply], list[Transaction]]: (updated supplies, transactions).
    """
    transactions: list[Transaction] = []
    for supply in supplies:
        supply.delivered = sold_items(
            delivered=supply.delivered,
            demand=demand[supply.market],
            total=total_delivered[supply.market],
        )
        transactions.append(
            Transaction(
                ts=supply.ts_finish,  # type: ignore
                cycle=cycle,
                user=supply.user,
                amount=supply.delivered * sell_prices[supply.market],
                description=f"Sell {supply.delivered} items of {market_names[supply.market]}",
            ),
        )
    return supplies, transactions


async def get_previous_owners(cycle: int, market_dao: MarketDAO) -> dict[tuple[int, int], int]:
    """Get previous owners for all markets.

    Args:
        cycle (int): current cycle.
        market_dao (MarketDAO): markets table DAO.

    Returns:
        dict[tuple[int, int], int]: {(market, position): user}.
    """
    prev_shares = await market_dao.select_shares(cycle=cycle - 1, nonzero=True)
    prev_owners_df = pd.DataFrame([share.dict() for share in prev_shares if share.position <= 2])
    prev_owners_df = prev_owners_df.set_index(["market", "position"])
    return prev_owners_df["user"].to_dict()


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
