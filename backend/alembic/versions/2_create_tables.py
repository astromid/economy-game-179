"""Created all necessary tables & fill them with initial data.

Revision ID: 2
Revises: 1
Create Date: 2022-10-07 17:32:00.000000

"""
import itertools
from datetime import datetime
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op
from passlib.context import CryptContext
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision = "2"
down_revision = "1"
branch_labels = None
depends_on = None

INITIAL_YAML_PATH = Path("alembic/initial_data.yaml")


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    initial_data = yaml.safe_load(INITIAL_YAML_PATH.read_text())
    initial_cycle = initial_data["initial_cycle"]
    player_ids = initial_data["player_ids"]
    npc_ids = initial_data["npc_ids"]

    create_users(initial_data["users"])
    create_markets(initial_data["markets"])
    create_unlocked_markets(initial_data["unlocked_markets"])
    create_cycles(initial_cycle)
    create_prices(initial_data["initial_market_prices"], cycle=initial_cycle)
    create_transactions(initial_cycle, initial_data["initial_player_balance"], player_ids)
    create_balances(initial_cycle, initial_data["initial_player_balance"], player_ids)
    create_stocks(initial_cycle, initial_data["initial_stocks_price"], player_ids + npc_ids)
    # supplies table doesn't have initial data
    op.create_table(
        "supplies",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts_start", sa.DateTime),
        sa.Column("ts_finish", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("declared_amount", sa.Integer, nullable=False),
        sa.Column("amount", sa.Integer),
    )
    create_products(
        player_ids=player_ids,
        n_markets=len(initial_data["markets"]),
        cycle=initial_cycle,
    )
    create_cycle_params(**initial_data["cycle_params"])
    # player modificators table doesn't have initial data
    op.create_table(
        "player_modificators",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("parameter", AutoString),
        sa.Column("value", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id", "market_id", "parameter"),
    )
    create_cycle_sync(player_ids)
    # ### end Alembic commands ###


def create_users(users: list[dict[str, int | str]]) -> None:
    # hash user passwords
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    for user in users:
        if user["password"] is not None:
            user["password"] = pwd_context.hash(user["password"])  # type: ignore
    # users table (root, players, NPCs)
    users_table = op.create_table(
        "users",
        sa.Column("id", sa.Integer, autoincrement=False, primary_key=True),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("login", sa.Text),
        sa.Column("password", sa.Text),
    )
    if users_table is not None:
        op.bulk_insert(users_table, users)
    else:
        raise RuntimeError("Failed to create users table")


def create_markets(markets: list[dict[str, int | str]]) -> None:
    # markets graph table (as an adjacency list)
    markets_table = op.create_table(
        "markets",
        sa.Column("id", sa.Integer, autoincrement=False, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("ring", sa.Integer, nullable=False),  # 2, 1, 0
        sa.Column("link1", sa.Integer),
        sa.Column("link2", sa.Integer),
        sa.Column("link3", sa.Integer),
        sa.Column("link4", sa.Integer),
        sa.Column("link5", sa.Integer),
    )
    if markets_table is not None:
        op.bulk_insert(markets_table, markets)
    else:
        raise RuntimeError("Failed to create markets table")


def create_unlocked_markets(unlocked_markets: list[dict[str, int]]) -> None:
    unlocked_markets_table = op.create_table(
        "unlocked_markets",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("protected", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("user_id", "market_id"),
    )
    if unlocked_markets_table is not None:
        op.bulk_insert(unlocked_markets_table, unlocked_markets)
    else:
        raise RuntimeError("Failed to create unlocked markets table")


def create_cycles(cycle: int) -> None:
    # game cycles table
    cycles_table = op.create_table(
        "cycles",
        sa.Column("cycle", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts_start", sa.DateTime),
        sa.Column("ts_finish", sa.DateTime),
    )
    if cycles_table is not None:
        op.bulk_insert(cycles_table, [{"cycle": cycle}])
    else:
        raise RuntimeError("Failed to create cycles table")


def create_prices(prices: list[dict[str, int | float]], cycle: int) -> None:
    prices_table = op.create_table(
        "prices",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("buy", sa.Float, nullable=False),
        sa.Column("sell", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "market_id"),
    )
    if prices_table is not None:
        for price in prices:
            price["cycle"] = cycle
        op.bulk_insert(prices_table, prices)
    else:
        raise RuntimeError("Failed to create prices table")


def create_transactions(cycle: int, amount: float, player_ids: list[int]) -> None:
    transactions_table = op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
    )
    if transactions_table is not None:
        transactions = [
            {
                "ts": datetime.now(),
                "cycle": cycle,
                "user_id": player_id,
                "amount": amount,
                "description": "Initial balance",
            }
            for player_id in player_ids
        ]
        op.bulk_insert(transactions_table, transactions)
    else:
        raise RuntimeError("Failed to create transactions table")


def create_balances(cycle: int, balance: float, player_ids: list[int]) -> None:
    balances_table = op.create_table(
        "balances",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    if balances_table is not None:
        balances = [{"cycle": cycle, "user_id": player_id, "amount": balance} for player_id in player_ids]
        op.bulk_insert(balances_table, balances)
    else:
        raise RuntimeError("Failed to create balances table")


def create_stocks(cycle: int, price: float, user_ids: list[int]) -> None:
    stocks_table = op.create_table(
        "stocks",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("price_noise", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    if stocks_table is not None:
        stocks = [{"cycle": cycle, "user_id": user_id, "price": price, "price_noise": price} for user_id in user_ids]
        op.bulk_insert(stocks_table, stocks)
    else:
        raise RuntimeError("Failed to create stocks table")


def create_products(player_ids: list[int], n_markets: int, cycle: int) -> None:
    products_table = op.create_table(
        "products",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("storage", sa.Integer, nullable=False),
        sa.Column("theta", sa.Float, nullable=False),
        sa.Column("share", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id", "market_id"),
    )
    if products_table is not None:
        products = [
            {"cycle": cycle, "user_id": user_id, "market_id": market_id, "storage": 0, "theta": 0, "share": 0}
            for user_id, market_id in itertools.product(player_ids, range(n_markets))
        ]
        op.bulk_insert(products_table, products)
    else:
        raise RuntimeError("Failed to create products table")


def create_cycle_params(
    alpha: float,
    alpha_multiplier: float,
    constant_params: dict[str, float | int],
    demand: dict[str, list[int]],
) -> None:
    cycle_params_table = op.create_table(
        "cycle_params",
        sa.Column("cycle", sa.Integer, primary_key=True),
        sa.Column("alpha", sa.Float, nullable=False),
        sa.Column("beta", sa.Float, nullable=False),
        sa.Column("gamma", sa.Float, nullable=False),
        sa.Column("tau_s", sa.Integer, nullable=False),
        sa.Column("coeff_h", sa.Integer, nullable=False),
        sa.Column("coeff_k", sa.Integer, nullable=False),
        sa.Column("coeff_l", sa.Integer, nullable=False),
        sa.Column("overdraft_rate", sa.Float, nullable=False),
        sa.Column("demand_ring0", sa.Integer, nullable=False),
        sa.Column("demand_ring1", sa.Integer, nullable=False),
        sa.Column("demand_ring2", sa.Integer, nullable=False),
    )
    if cycle_params_table is not None:
        cycles = range(1, len(demand["ring0"]) + 1)
        alphas = [round(alpha * alpha_multiplier ** (cycle - 1), 3) for cycle in cycles]
        cycle_params = [
            {
                "cycle": cycle,
                "alpha": alphas[cycle - 1],
                "demand_ring2": demand["ring2"][cycle - 1],
                "demand_ring1": demand["ring1"][cycle - 1],
                "demand_ring0": demand["ring0"][cycle - 1],
                **constant_params,
            }
            for cycle in cycles
        ]
        op.bulk_insert(cycle_params_table, cycle_params)
    else:
        raise RuntimeError("Failed to create cycle_params table")


def create_cycle_sync(player_ids: list[int]) -> None:
    sync_table = op.create_table(
        "cycle_sync",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("synced", sa.Boolean, nullable=False),
    )
    if sync_table is not None:
        initial_sync = [{"user_id": player_id, "synced": False} for player_id in player_ids]
        op.bulk_insert(sync_table, initial_sync)
    else:
        raise RuntimeError("Failed to create cycle sync table")


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    tables = (
        "cycle_sync",
        "player_modificators",
        "cycle_params",
        "products",
        "supplies",
        "stocks",
        "balances",
        "transactions",
        "prices",
        "cycles",
        "unlocked_markets",
        "markets",
        "users",
    )
    for table in tables:
        op.drop_table(table)
    # ### end Alembic commands ###
