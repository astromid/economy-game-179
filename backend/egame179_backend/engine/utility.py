import pandas as pd

from egame179_backend.db import BalanceDAO, MarketDAO, WarehouseDAO, WorldDemandDAO


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
    if prev_owners_df.empty:
        return {}
    prev_owners_df = prev_owners_df.set_index(["market", "position"])
    return prev_owners_df["user"].to_dict()
