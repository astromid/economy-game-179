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
    balance = await balance_dao.get(user=user, cycle=cycle)
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
    storage = await wh_dao.get(user=user, cycle=cycle, market=market)
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


async def get_supply_velocities(
    market_dao: MarketDAO,
    wd_dao: WorldDemandDAO,
    cycle: int,
    tau_s: int,
) -> dict[int, float]:
    """Get supply velocities for all markets.

    Args:
        market_dao (MarketDAO): markets table DAO.
        wd_dao (WorldDemandDAO): world_demand table DAO.
        cycle (int): current cycle.
        tau_s (int): time of full supply.

    Returns:
        dict[int, float]: {market: velocity}.
    """
    market2ring = await get_market_rings(market_dao)
    demand = await wd_dao.select(cycle)
    return {market: demand[ring] / tau_s for market, ring in market2ring.items()}
