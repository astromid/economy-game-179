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
)
from egame179_backend.engine.math import sold_items
from egame179_backend.engine.utility import get_fee_mods, get_market_names, get_previous_owners, get_world_demand


async def finish_cycle(  # noqa: WPS213, WPS217
    cycle: Cycle,
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    mod_dao: db.FeeModificatorDAO,
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
        mod_dao (db.FeeModificatorDAO): fee_modificators table DAO.
        price_dao (db.MarketPriceDAO): prices table DAO.
        supply_dao (db.SupplyDAO): supplies table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wd_dao (db.WorldDemandDAO): world_demands table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
    """
    # 1. Finish ongoing supplies, calculate deliveries
    demand = await get_world_demand(market_dao=market_dao, wd_dao=wd_dao, cycle=cycle.id)
    supplies = await process_supplies(cycle=cycle, demand=demand, supply_dao=supply_dao)
    ic("Stage 1: supplies finished")

    # 2. Storage fees
    await process_storage_fees(cycle=cycle, mod_dao=mod_dao, wh_dao=wh_dao, transaction_dao=transaction_dao)
    ic("Stage 2: storage fees")

    # 3. Life fees
    await process_life_fees(cycle=cycle, balance_dao=balance_dao, mod_dao=mod_dao, transaction_dao=transaction_dao)
    ic("Stage 3: life fees")

    # 4. Overdraft fees
    await process_overdrafts(cycle=cycle, balance_dao=balance_dao, transaction_dao=transaction_dao)
    ic("Stage 4: overdraft fees")

    # 5. Process supply transactions
    await process_supply_transactions(
        cycle=cycle.id,
        supplies=supplies,
        market_dao=market_dao,
        price_dao=price_dao,
        transaction_dao=transaction_dao,
    )
    ic("Stage 5: supply transactions")

    # 6. Calculate market shares and positions
    await process_market_shares(
        cycle=cycle.id,
        supplies_df=pd.DataFrame([supply.dict() for supply in supplies]),
        market_dao=market_dao,
    )
    ic("Stage 6: market shares & positions")


async def process_supplies(cycle: Cycle, demand: dict[int, int], supply_dao: db.SupplyDAO) -> list[Supply]:
    """Finish ongoing supplies, calculate deliveries.

    Args:
        cycle (Cycle): current cycle.
        demand (dict[int, int]): demand for each market.
        supply_dao (db.SupplyDAO): supplies table DAO.

    Raises:
        ValueError: if cycle is not finished yet.

    Returns:
        list[Supply]: updated supplies.
    """
    if cycle.ts_finish is None:
        raise ValueError("Cycle is not finished yet")
    supplies = await supply_dao.select(cycle=cycle.id, ongoing=True)
    supplies, total_delivered = calculate_delivered(
        supplies=supplies,
        ts_finish=cycle.ts_finish,
        velocities={market: demand / cycle.tau_s for market, demand in demand.items()},
    )
    # calculate sold items in case of market overflow
    for supply in supplies:
        supply.sold = sold_items(
            delivered=supply.delivered,
            demand=demand[supply.market],
            total=total_delivered[supply.market],
        )
    ic("Final supplies:", supplies)
    await supply_dao.update(supplies)
    return supplies


async def process_storage_fees(
    cycle: Cycle,
    mod_dao: db.FeeModificatorDAO,
    transaction_dao: db.TransactionDAO,
    wh_dao: db.WarehouseDAO,
) -> None:
    """Process storage fees for the cycle.

    Args:
        cycle (Cycle): current cycle.
        mod_dao (db.FeeModificatorDAO): fee_modificators table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
        wh_dao (db.WarehouseDAO): warehouses table DAO.
    """
    fee_mods = await get_fee_mods(cycle=cycle.id, fee="gamma", mod_dao=mod_dao)
    warehouses = await wh_dao.select(cycle=cycle.id)
    total_storage: dict[int, int] = defaultdict(int)
    for wh in warehouses:
        total_storage[wh.user] += wh.quantity
    transactions = [
        Transaction(
            ts=cycle.ts_finish,  # type: ignore
            cycle=cycle.id,
            user=user,
            amount=-cycle.gamma * fee_mods.get(user, 1) * storage,
            description=f"Storage fee ({storage} items, ({cycle.gamma} x {fee_mods.get(user, 1)}) / item)",
        )
        for user, storage in total_storage.items()
    ]
    ic("Storage fee transactions:", transactions)
    await transaction_dao.add(transactions)


async def process_life_fees(
    cycle: Cycle,
    balance_dao: db.BalanceDAO,
    mod_dao: db.FeeModificatorDAO,
    transaction_dao: db.TransactionDAO,
) -> None:
    """Process life fees for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        mod_dao (db.FeeModificatorDAO): fee_modificators table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
    """
    fee_mods = await get_fee_mods(cycle=cycle.id, fee="alpha", mod_dao=mod_dao)
    balances = await balance_dao.select(cycle=cycle.id)
    transactions = [
        Transaction(
            ts=cycle.ts_finish,  # type: ignore
            cycle=cycle.id,
            user=balance.user,
            amount=-cycle.alpha * fee_mods.get(balance.user, 1),
            description=f"Life fee ({cycle.alpha} x {fee_mods.get(balance.user, 1)})",
        )
        for balance in balances
    ]
    ic("Life fee transactions:", transactions)
    await transaction_dao.add(transactions)


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


async def process_supply_transactions(
    cycle: int,
    supplies: list[Supply],
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    transaction_dao: db.TransactionDAO,
) -> None:
    """Process supply transactions.

    Args:
        cycle (int): finished cycle.
        supplies (list[Supply]): supplies.
        market_dao (db.MarketDAO): markets table DAO.
        price_dao (db.MarketPriceDAO): prices table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
    """
    market_names = await get_market_names(market_dao=market_dao)
    prices = await price_dao.select(cycle=cycle)
    sell_prices = {price.market: price.sell for price in prices}
    transactions = [
        Transaction(
            ts=supply.ts_finish,  # type: ignore
            cycle=cycle,
            user=supply.user,
            amount=supply.sold * sell_prices[supply.market],
            description=f"Sell {supply.sold} items of {market_names[supply.market]}",
        )
        for supply in supplies
    ]
    ic("Sell transactions:", transactions)
    await transaction_dao.add(transactions)


async def process_market_shares(cycle: int, supplies_df: pd.DataFrame, market_dao: db.MarketDAO) -> None:
    """Process market shares for the cycle.

    Args:
        cycle (int): current cycle.
        supplies_df (pd.DataFrame): dataframe with supplies.
        market_dao (db.MarketDAO): markets table DAO.
    """
    shares = await market_dao.select_shares(cycle=cycle)
    previous_owners = await get_previous_owners(cycle=cycle, market_dao=market_dao)

    if supplies_df.empty:
        sold_per_user_market = {}
        sold_per_market = {}
    else:
        sold_per_user_market = supplies_df.groupby(["user", "market"])["sold"].sum().to_dict()
        sold_per_market = supplies_df.groupby("market")["sold"].sum().to_dict()

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
    cycle: Cycle,  # finished cycle, prev = -1, next = +1
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
    # 7. Calculate new prices
    prod_df = await process_prices(
        cycle=cycle,
        market_dao=market_dao,
        price_dao=price_dao,
        production_dao=production_dao,
        supply_dao=supply_dao,
        wd_dao=wd_dao,
    )
    ic("Stage 7: new market prices")

    # 8. Update thetas
    await process_thetas(cycle=cycle, prod_df=prod_df, theta_dao=theta_dao)
    ic("Stage 7: new thetas")

    # 9. Unlock markets by top1/top2 share & home markets
    await process_unlocks(cycle=cycle, market_dao=market_dao)
    ic("Stage 9: new unlocked markets")

    # 10. Make auxiliary production & transactions
    await process_auxiliary(
        cycle=cycle,
        balance_dao=balance_dao,
        market_dao=market_dao,
        production_dao=production_dao,
        transaction_dao=transaction_dao,
    )
    ic("Stage 10: auxiliary production")

    # 11. Calculate new stocks
    await process_stocks(
        cycle=cycle.id,
        balance_dao=balance_dao,
        market_dao=market_dao,
        stock_dao=stock_dao,
        transaction_dao=transaction_dao,
        wh_dao=wh_dao,
    )
    ic("Stage 11: new stocks")


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
        if share.position == 1:
            new_unlocks[share.user, share.market] = True
            for node in graph.neighbors(share.market):
                new_unlocks[share.user, node] = True
        elif not new_unlocks.get((share.user, share.market), False):
            new_unlocks[share.user, share.market] = False
    ic(new_unlocks)
    await market_dao.create_shares(cycle=cycle.id + 1, new_unlocks=new_unlocks)


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
        npc_df=pd.DataFrame(npcs.items(), columns=["market", "npc"]),
        initial_balance=init_balance,
    )
    ic("New stocks", new_stocks)
    await stock_dao.create(cycle=cycle + 1, new_stocks=new_stocks)


async def process_auxiliary(
    cycle: Cycle,
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    production_dao: db.ProductionDAO,
    transaction_dao: db.TransactionDAO,
) -> None:
    """Process auxiliary production & transactions for the cycle.

    Args:
        cycle (Cycle): finished cycle.
        balance_dao (db.BalanceDAO): balances table DAO.
        market_dao (db.MarketDAO): markets table DAO.
        production_dao (db.ProductionDAO): production table DAO.
        transaction_dao (db.TransactionDAO): transactions table DAO.
    """
    balances = await balance_dao.select(cycle=cycle.id)
    markets = await market_dao.select_markets()
    await production_dao.create_auxiliary(
        cycle=cycle.id + 1,
        users=[balance.user for balance in balances],
        markets=[market.id for market in markets],
    )
    await transaction_dao.add(
        [
            Transaction(
                ts=cycle.ts_finish,  # type: ignore
                cycle=cycle.id + 1,
                user=bal.user,
                amount=0,
                description="Ugly hack",
            )
            for bal in balances
        ],
    )
