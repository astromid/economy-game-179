from collections import defaultdict

import pandas as pd
from icecream import ic

from egame179_backend import db
from egame179_backend.db.cycle import Cycle
from egame179_backend.db.market import MarketShare
from egame179_backend.db.supply import Supply
from egame179_backend.db.transaction import Transaction
from egame179_backend.engine.calc import (
    calculate_delivered,
    calculate_new_prices,
    calculate_new_stocks,
    calculate_new_thetas,
    calculate_shares,
    calculate_sold,
)
from egame179_backend.engine.utility import get_market_names, get_previous_owners, get_world_demand


async def finish_cycle(
    cycle: Cycle,
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    supply_dao: db.SupplyDAO,
    transaction_dao: db.TransactionDAO,
    wd_dao: db.WorldDemandDAO,
    wh_dao: db.WarehouseDAO,
) -> None:
    """Finish cycle. Calculate deliveries, sales, storage fees and market shares.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        market_dao (db.MarketDAO): markets table DAO.
        price_dao (db.MarketPriceDAO): prices table DAO.
        supply_dao (db.SupplyDAO): supplies table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wd_dao (db.WorldDemandDAO): world_demands table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
    """
    # 1. Finish ongoing supplies, calculate deliveries
    demand = await get_world_demand(market_dao=market_dao, wd_dao=wd_dao, cycle=cycle.id)
    supplies = await process_supplies(
        cycle=cycle,
        demand=demand,
        supply_dao=supply_dao,
        market_dao=market_dao,
        price_dao=price_dao,
        transaction_dao=transaction_dao,
    )
    supplies_df = pd.DataFrame([supply.dict() for supply in supplies])
    ic("Stage 1: processing supplies finished")

    # 2. Storage fees
    await process_storage_fees(cycle=cycle, wh_dao=wh_dao, transaction_dao=transaction_dao)
    ic("Stage 2: processing storage fees finished")

    # 3. Life fees
    await process_life_fees(cycle=cycle, balance_dao=balance_dao, transaction_dao=transaction_dao)
    ic("Stage 3: processing life fees finished")

    # 4. Calculate market shares and positions
    await process_market_shares(cycle=cycle.id, supplies_df=supplies_df, market_dao=market_dao)
    ic("Stage 4: processing market shares finished")


async def process_supplies(
    cycle: Cycle,
    demand: dict[int, int],
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    supply_dao: db.SupplyDAO,
    transaction_dao: db.TransactionDAO,
) -> list[Supply]:
    """Finish ongoing supplies, calculate deliveries, make transactions.

    Args:
        cycle (Cycle): current cycle.
        demand (dict[int, int]): demand for each market.
        market_dao (db.MarketDAO): markets table DAO.
        price_dao (db.MarketPriceDAO): market_prices table DAO.
        supply_dao (db.SupplyDAO): supplies table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.

    Raises:
        ValueError: if cycle is not finished yet.

    Returns:
        list[Supply]: updated supplies.
    """
    if cycle.ts_finish is None:
        raise ValueError("Cycle is not finished yet")
    market_names = await get_market_names(market_dao=market_dao)
    prices = await price_dao.select(cycle=cycle.id)
    sell_prices = {price.market: price.sell for price in prices}

    supplies = await supply_dao.select(cycle=cycle.id, ongoing=True)
    supplies, total_delivered = calculate_delivered(
        supplies=supplies,
        ts_finish=cycle.ts_finish,
        velocities={market: demand / cycle.tau_s for market, demand in demand.items()},
    )
    # calculate real deliveries in case of market overflow & make sell transactions
    supplies, transactions = calculate_sold(
        cycle=cycle.id,
        supplies=supplies,
        demand=demand,
        total_delivered=total_delivered,
        sell_prices=sell_prices,
        market_names=market_names,
    )
    ic("Final supplies:", supplies)
    ic("Sell transactions:", transactions)

    await supply_dao.update(supplies)
    await transaction_dao.add(transactions)
    return supplies


async def process_storage_fees(cycle: Cycle, transaction_dao: db.TransactionDAO, wh_dao: db.WarehouseDAO) -> None:
    """Process storage fees for the cycle.

    Args:
        cycle (Cycle): current cycle.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
    """
    warehouses = await wh_dao.select(cycle=cycle.id)
    total_storage: dict[int, int] = defaultdict(int)
    for wh in warehouses:
        total_storage[wh.user] += wh.quantity
    transactions = [
        Transaction(
            ts=cycle.ts_finish,  # type: ignore
            cycle=cycle.id,
            user=user,
            amount=-cycle.gamma * storage,
            description=f"Storage fee ({storage} items, {cycle.gamma} / item)",
        )
        for user, storage in total_storage.items()
    ]
    ic("Storage fee transactions:", transactions)
    await transaction_dao.add(transactions)


async def process_life_fees(cycle: Cycle, balance_dao: db.BalanceDAO, transaction_dao: db.TransactionDAO) -> None:
    """Process life fees for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
    """
    balances = await balance_dao.select(cycle=cycle.id)
    transactions = [
        Transaction(
            ts=cycle.ts_finish,  # type: ignore
            cycle=cycle.id,
            user=balance.user,
            amount=-cycle.alpha,
            description="Life fee",
        )
        for balance in balances
    ]
    ic("Life fee transactions:", transactions)
    await transaction_dao.add(transactions)


async def process_market_shares(cycle: int, supplies_df: pd.DataFrame, market_dao: db.MarketDAO) -> None:
    """Process market shares for the cycle.

    Args:
        cycle (int): current cycle.
        supplies_df (pd.DataFrame): dataframe with supplies.
        market_dao (db.MarketDAO): markets table DAO.
    """
    shares = await market_dao.select_shares(cycle=cycle)
    sold_per_user_market = supplies_df.groupby(["user", "market"])["delivered"].sum().to_dict()
    sold_per_market = supplies_df.groupby("market")["delivered"].sum().to_dict()
    previous_owners = await get_previous_owners(cycle=cycle, market_dao=market_dao)

    ic(previous_owners)
    ic(sold_per_user_market)
    ic(sold_per_market)

    market_shares = calculate_shares(
        shares=shares,
        sold_per_market=sold_per_market,
        sold_per_user_market=sold_per_user_market,
        previous_owners=previous_owners,
    )
    updated_shares: list[MarketShare] = []
    for _, mshares in market_shares.items():
        sorted_shares = sorted(mshares, key=lambda shr: shr.share, reverse=True)
        for pos, share in enumerate(sorted_shares, start=1):
            share.position = pos
            updated_shares.append(share)
    ic(updated_shares)
    await market_dao.update_shares(updated_shares)


async def prepare_new_cycle(  # noqa: WPS211, WPS213, WPS217
    cycle: Cycle,  # finished cycle, prev_prev = -1, next = +1
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    production_dao: db.ProductionDAO,
    supply_dao: db.SupplyDAO,
    stock_dao: db.StockDAO,
    theta_dao: db.ThetaDAO,
    transaction_dao: db.TransactionDAO,
    wh_dao: db.WarehouseDAO,
    wd_dao: db.WorldDemandDAO,
) -> None:
    """Prepare new cycle.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        market_dao (db.MarketDAO): markets table DAO.
        price_dao (db.MarketPriceDAO): market prices table DAO.
        production_dao (db.ProductionDAO): productions table DAO.
        supply_dao (db.SupplyDAO): supplies table DAO.
        stock_dao (db.StockDAO): stocks table DAO.
        theta_dao (db.ThetaDAO): thetas table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
        wd_dao (db.WorldDemandDAO): world demands table DAO.
    """
    # 5. Calculate new prices
    prod_df = await process_prices(
        cycle=cycle,
        market_dao=market_dao,
        price_dao=price_dao,
        production_dao=production_dao,
        supply_dao=supply_dao,
        wd_dao=wd_dao,
    )
    ic("Stage 5: new market prices")

    # 6. Update thetas
    await process_thetas(cycle=cycle, prod_df=prod_df, theta_dao=theta_dao)
    ic("Stage 6: new thetas")

    # 7. Unlock markets by top1/top2 share & home markets
    await process_unlocks(cycle=cycle, market_dao=market_dao)
    ic("Stage 7: new unlocked markets")

    # 8. Process overdraft fees
    await process_overdrafts(cycle=cycle, balance_dao=balance_dao, transaction_dao=transaction_dao)
    ic("Stage 8: overdraft fees")

    # 9. Calculate new stocks
    await process_stocks(
        cycle=cycle.id,
        balance_dao=balance_dao,
        market_dao=market_dao,
        stock_dao=stock_dao,
        transaction_dao=transaction_dao,
        wh_dao=wh_dao,
    )
    ic("Stage 9: new stocks")

    # 10. Make auxiliary production
    await process_auxiliary_production(
        cycle=cycle.id,
        balance_dao=balance_dao,
        market_dao=market_dao,
        production_dao=production_dao,
    )
    ic("Stage 10: auxiliary production")


async def process_prices(
    cycle: Cycle,
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    production_dao: db.ProductionDAO,
    supply_dao: db.SupplyDAO,
    wd_dao: db.WorldDemandDAO,
) -> pd.DataFrame:
    """Process new prices for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        market_dao (db.MarketDAO): markets table DAO.
        price_dao (db.MarketPriceDAO): prices table DAO.
        production_dao (db.ProductionDAO): production table DAO.
        supply_dao (db.SupplyDAO): supplies table DAO.
        wd_dao (db.WorldDemandDAO): world demand table DAO.

    Returns:
        pd.DataFrame: production dataframe for futher theta calculation.
    """
    prices = await price_dao.select(cycle=cycle.id)
    supplies = await supply_dao.select(cycle=cycle.id)
    demand = await get_world_demand(cycle=cycle.id, market_dao=market_dao, wd_dao=wd_dao)
    production = await production_dao.select()

    prod_df = pd.DataFrame([prod.dict() for prod in production if prod.cycle >= cycle.id - 2])
    new_prices = calculate_new_prices(
        cycle=cycle,
        prices=prices,
        prod_df=prod_df,
        supp_df=pd.DataFrame([supp.dict() for supp in supplies]),
        demand=demand,
    )
    await price_dao.create(cycle=cycle.id + 1, new_prices=new_prices)
    ic(new_prices)
    return prod_df


async def process_thetas(cycle: Cycle, prod_df: pd.DataFrame, theta_dao: db.ThetaDAO) -> None:
    """Process new thetas for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        prod_df (pd.DataFrame): production dataframe.
        theta_dao (db.ThetaDAO): thetas table DAO.
    """
    thetas = await theta_dao.select(cycle=cycle.id)
    new_thetas = calculate_new_thetas(cycle=cycle, thetas=thetas, prod_df=prod_df)
    ic(new_thetas)
    await theta_dao.create(cycle=cycle.id + 1, new_thetas=new_thetas)


async def process_unlocks(cycle: Cycle, market_dao: db.MarketDAO) -> None:
    """Process new unlocks for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        market_dao (db.MarketDAO): markets table DAO.
    """
    graph = await market_dao.get_graph()
    shares = await market_dao.select_shares(cycle=cycle.id)
    new_unlocks: dict[tuple[int, int], bool] = {}
    for share in shares:
        if share.position in {1, 2}:
            new_unlocks[share.user, share.market] = True
            for node in graph.neighbors(share.market):
                new_unlocks[share.user, node] = True
        else:
            new_unlocks[share.user, share.market] = False
    ic(new_unlocks)
    await market_dao.create_shares(cycle=cycle.id + 1, new_unlocks=new_unlocks)


async def process_overdrafts(cycle: Cycle, balance_dao: db.BalanceDAO, transaction_dao: db.TransactionDAO) -> None:
    """Process overdraft fees for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
    """
    balances = await balance_dao.select(cycle=cycle.id)
    transactions = [
        Transaction(
            ts=cycle.ts_finish,  # type: ignore
            cycle=cycle.id,
            user=balance.user,
            amount=balance.balance * cycle.overdraft_rate,  # balance is already negative
            description="Overdraft fee",
        )
        for balance in balances
        if balance.balance < 0
    ]
    ic("Overdraft fees:", transactions)
    await transaction_dao.add(transactions)


async def process_stocks(  # noqa: WPS217
    cycle: int,
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    stock_dao: db.StockDAO,
    transaction_dao: db.TransactionDAO,
    wh_dao: db.WarehouseDAO,
) -> None:
    """Process new stocks for the cycle.

    Args:
        cycle (int): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        market_dao (db.MarketDAO): markets table DAO.
        stock_dao (db.StockDAO): stocks table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
    """
    stocks = await stock_dao.select(cycle=cycle)
    balances = await balance_dao.select()
    storages = await wh_dao.select()
    npcs = await market_dao.get_market_npcs()
    init_balance = await transaction_dao.get_init_balance()

    new_stocks = calculate_new_stocks(
        cycle=cycle,
        stocks=stocks,
        balances_df=pd.DataFrame([balance.dict() for balance in balances if balance.cycle >= cycle - 1]),
        storages_df=pd.DataFrame([storage.dict() for storage in storages if storage.cycle >= cycle - 1]),
        npc_df=pd.DataFrame(npcs, columns=["market", "user"]),
        initial_balance=init_balance,
    )
    ic("New stocks", new_stocks)
    await stock_dao.create(cycle=cycle + 1, new_stocks=new_stocks)


async def process_auxiliary_production(
    cycle: int,
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    production_dao: db.ProductionDAO,
) -> None:
    """Process auxiliary production for the cycle.

    Args:
        cycle (int): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        market_dao (db.MarketDAO): markets table DAO.
        production_dao (db.ProductionDAO): production table DAO.
    """
    balances = await balance_dao.select(cycle=cycle)
    markets = await market_dao.select_markets()
    await production_dao.create_auxiliary(
        cycle=cycle + 1,
        users=[balance.user for balance in balances],
        markets=[market.id for market in markets],
    )