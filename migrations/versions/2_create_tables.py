"""Created all necessary tables & fill them with initial data.

Revision ID: 2
Revises: 1
Create Date: 2022-10-07 17:32:00.000000

"""
import itertools
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op

# revision identifiers, used by Alembic.
revision = "2"
down_revision = "1"
branch_labels = None
depends_on = None

INITIAL_YAML_PATH = Path("migrations/initial_data.yaml")


def upgrade() -> None:
    initial_data = yaml.safe_load(INITIAL_YAML_PATH.read_text())
    initial_cycle = initial_data["initial_cycle"]

    users_table = create_users(initial_data["users"])
    player_ids = get_user_ids(users_table, user_type="player")
    npc_ids = get_user_ids(users_table, user_type="npc")

    create_cycles(initial_cycle)
    create_markets(initial_data["markets"])
    create_prices(initial_data["initial_market_prices"])
    create_transactions(initial_cycle, initial_data["initial_player_balance"], player_ids)
    create_balances(initial_cycle, initial_data["initial_player_balance"], player_ids)
    create_stocks(initial_cycle, initial_data["initial_stocks_price"], player_ids + npc_ids)
    # logistic operations table doesn't have initial data
    op.create_table(
        "logistic_ops",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("description", sa.Text),
    )
    create_products(
        n_players=len(player_ids),
        n_markets=len(initial_data["markets"]),
        initial_cycle=initial_cycle,
        initial_theta=initial_data["initial_theta"],
    )
    create_cycle_params(**initial_data["cycle_params"])
    # player modificators table doesn't have initial data
    op.create_table(
        "player_modificators",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("parameter", sa.Text, nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id", "market_id", "parameter"),
    )


def create_users(users: list[dict[str, str]]) -> sa.Table:
    # users table (root, players, NPCs)
    users_table = op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("login", sa.Text),
        sa.Column("password", sa.Text),
    )
    if users_table is not None:
        op.bulk_insert(users_table, users)
        return users_table
    raise RuntimeError("Failed to create users table")


def get_user_ids(users_table: sa.Table, user_type: str) -> list[int]:
    con = op.get_bind()
    stmt = sa.select([users_table.c.id]).where(users_table.c.type == user_type)
    return [row["id"] for row in con.execute(stmt)]


def create_cycles(initial_cycle: int) -> None:
    # game cycles table
    cycles_table = op.create_table(
        "cycles",
        sa.Column("cycle", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("started", sa.DateTime),
        sa.Column("finished", sa.DateTime),
    )
    if cycles_table is not None:
        op.bulk_insert(cycles_table, [{"cycle": initial_cycle}])
    else:
        raise RuntimeError("Failed to create cycles table")


def create_markets(markets: list[dict[str, int | str]]) -> None:
    # markets graph table (as an adjacency list)
    markets_table = op.create_table(
        "markets",
        sa.Column("id", sa.Integer, primary_key=True),
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


def create_prices(initial_prices: list[dict[str, int | float]]) -> None:
    prices_table = op.create_table(
        "prices",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("buy", sa.Float, nullable=False),
        sa.Column("sell", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "market_id"),
    )
    if prices_table is not None:
        op.bulk_insert(prices_table, initial_prices)
    else:
        raise RuntimeError("Failed to create prices table")


def create_transactions(initial_cycle: int, initial_balance: float, player_ids: list[int]) -> None:
    transactions = [
        {"cycle": initial_cycle, "user_id": player_id, "amount": initial_balance, "description": "Initial balance"}
        for player_id in player_ids
    ]
    transactions_table = op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text),
    )
    if transactions_table is not None:
        op.bulk_insert(transactions_table, transactions)
    else:
        raise RuntimeError("Failed to create transactions table")


def create_balances(initial_cycle: int, initial_balance: float, player_ids: list[int]) -> None:
    balances = [{"cycle": initial_cycle, "user_id": player_id, "amount": initial_balance} for player_id in player_ids]
    balances_table = op.create_table(
        "balances",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    if balances_table is not None:
        op.bulk_insert(balances_table, balances)
    else:
        raise RuntimeError("Failed to create balances table")


def create_stocks(initial_cycle: int, initial_stock_price: float, user_ids: list[int]) -> None:
    stocks = [{"cycle": initial_cycle, "user_id": user_id, "price": initial_stock_price} for user_id in user_ids]
    stocks_table = op.create_table(
        "stocks",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("price", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    if stocks_table is not None:
        op.bulk_insert(stocks_table, stocks)
    else:
        raise RuntimeError("Failed to create stocks table")


def create_products(n_players: int, n_markets: int, initial_cycle: int, initial_theta: float) -> None:
    user_market_combs = itertools.product(range(n_players), range(n_markets))
    products = [
        {"cycle": initial_cycle, "user_id": user_id, "market_id": market_id, "storage": 0, "theta": initial_theta}
        for user_id, market_id in user_market_combs
    ]
    products_table = op.create_table(
        "products",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("storage", sa.Integer, nullable=False),
        sa.Column("theta", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id", "market_id"),
    )
    if products_table is not None:
        op.bulk_insert(products_table, products)
    else:
        raise RuntimeError("Failed to create products table")


def create_cycle_params(
    initial_alpha: float,
    alpha_multiplier: float,
    beta: float,
    gamma: float,
    tau_sec: int,
    demand: dict[str, list[int]],
) -> None:
    cycles = len(demand["ring0"])
    alphas = [round(initial_alpha * alpha_multiplier ** cycle, 3) for cycle in range(cycles)]
    cycle_params = [
        {
            "cycle": cycle,
            "alpha": alphas[cycle],
            "beta": beta,
            "gamma": gamma,
            "tau_sec": tau_sec,
            "demand_ring2": demand["ring2"][cycle],
            "demand_ring1": demand["ring1"][cycle],
            "demand_ring0": demand["ring0"][cycle],
        }
        for cycle in range(cycles)
    ]
    cycle_params_table = op.create_table(
        "cycle_params",
        sa.Column("cycle", sa.Integer, primary_key=True),
        sa.Column("alpha", sa.Float, nullable=False),
        sa.Column("beta", sa.Float, nullable=False),
        sa.Column("gamma", sa.Float, nullable=False),
        sa.Column("tau_s", sa.Integer, nullable=False),
        sa.Column("demand_ring2", sa.Integer, nullable=False),
        sa.Column("demand_ring1", sa.Integer, nullable=False),
        sa.Column("demand_ring0", sa.Integer, nullable=False),
    )
    if cycle_params_table is not None:
        op.bulk_insert(cycle_params_table, cycle_params)
    else:
        raise RuntimeError("Failed to create cycle_params table")


def downgrade() -> None:
    tables = (
        "player_modificators",
        "cycle_params",
        "products",
        "logistic_ops",
        "stocks",
        "balances",
        "transactions",
        "prices",
        "markets",
        "cycles",
        "users",
    )
    for table in tables:
        op.drop_table(table)
