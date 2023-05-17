from collections import defaultdict

import pandas as pd
from icecream import ic

from egame179_backend import db
from egame179_backend.db.cycle import Cycle
from egame179_backend.db.market import MarketShare
from egame179_backend.db.supply import Supply
from egame179_backend.db.transaction import Transaction
from egame179_backend.engine.utility import (
    calculate_delivered,
    calculate_shares,
    calculate_sold,
    get_market_names,
    get_previous_owners,
    get_world_demand,
)


async def finish_cycle(
    cycle: Cycle,
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
    # 3. Calculate market shares and positions
    await process_market_shares(cycle=cycle.id, supplies_df=supplies_df, market_dao=market_dao)
    ic("Stage 3: processing market shares finished")


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


async def prepare_cycle(
    cycle: Cycle,  # new cycle, finished = -1, prev = -2
    balance_dao: db.BalanceDAO,
    market_dao: db.MarketDAO,
    price_dao: db.MarketPriceDAO,
    production_dao: db.ProductionDAO,
    supply_dao: db.SupplyDAO,
    transaction_dao: db.TransactionDAO,
) -> None:
    # 1. Calculate new prices
    prices = await price_dao.get_all(cycle=cycle - 1)
    market2price = {price.market_id: price for price in prices}
    transactions = await transaction_dao.get(user_id=None)
    demands = get_demands(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=cycle_params,
    )
    # take transactions from last 3 cycles
    transactions_df = pd.DataFrame([tr.dict() for tr in transactions if tr.cycle >= cycle - 3])
    transactions_df = transactions_df.dropna(subset=["market_id", "items"]).astype({"market_id": int, "items": int})
    # buy for last 3 cycles, sell only for last cycle
    buy_df = transactions_df[transactions_df["amount"] < 0]
    sell_df = transactions_df[(transactions_df["amount"] > 0) & (transactions_df["cycle"] == cycle - 1)]

    buy_market = buy_df[buy_df["cycle"] == cycle - 1].groupby("market_id")["items"].sum().to_dict()
    buy_market_prev = buy_df[buy_df["cycle"] == cycle - 2].groupby("market_id")["items"].sum().to_dict()
    sell_market = sell_df.groupby("market_id")["items"].sum().to_dict()

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

    # 2. Update products (theta, storage, market share)
    products = await product_dao.get_all(cycle=cycle - 1)
    buy_cycle_sum_df = buy_df.groupby(["user_id", "market_id", "cycle"])["items"].sum().reset_index()
    buy_mean = buy_cycle_sum_df.groupby(["user_id", "market_id"])["items"].mean().to_dict()
    # ! check validity of using amount vs. real_amount
    sell_by_user = sell_df.groupby(["user_id", "market_id"])["items"].sum().to_dict()

    from icecream import ic
    ic(buy_cycle_sum_df)
    ic(buy_mean)
    ic(sell_by_user)

    market_shares: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for product in products:
        share = sell_by_user.get((product.user_id, product.market_id), 0) / sell_market.get(product.market_id, 1)
        market_shares[product.market_id].append((product.user_id, share))
        await product_dao.add(
            Product(
                cycle=cycle,
                user_id=product.user_id,
                market_id=product.market_id,
                storage=product.storage,
                theta=theta_next(buy_mean.get((product.user_id, product.market_id), 0), k=cycle_params.coeff_k),
                share=share,
            ),
        )
    ic(market_shares)

    market_shares = {m_id: [share for share in shares if share[1] > 0] for m_id, shares in market_shares.items()}
    ic(market_shares)

    # 3. Unlock markets by top1/top2 share
    sorted_shares = {m_id: sorted(market_shares[m_id], key=lambda x: x[1], reverse=True) for m_id in market_shares}
    top_shares = {m_id: [share[0] for share in sorted_shares[m_id][:2]] for m_id in sorted_shares}

    ic(sorted_shares)
    ic(top_shares)

    # step1: lock all unprotected markets
    unlocked_markets = await unlocked_market_dao.get_all()
    for um in unlocked_markets:
        await unlocked_market_dao.lock(user_id=um.user_id, market_id=um.market_id)

    # step2: unlock top-shared markets and their links
    m_id2market = {market.id: market for market in markets}
    for m_id, top_users in top_shares.items():
        for user_id in top_users:
            market = m_id2market[m_id]
            to_unlock = {m_id, market.link1, market.link2, market.link3, market.link4, market.link5}
            for um_id in to_unlock:
                if um_id is not None:
                    await unlocked_market_dao.unlock(user_id=user_id, market_id=um_id)


async def life_overdraft_fees() -> None:
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
