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
    users = initial_data["users"]
    # tables with initial data
    create_users(users)
    create_sync_status(users)
    create_npcs(initial_data["npcs"])
    create_cycles(**initial_data["cycles"])
    create_markets(initial_data["markets"])
    create_market_connections(initial_data["market_connections"])
    create_market_prices(initial_data["market_prices"])
    create_market_shares(users, initial_data["markets"])
    create_world_demand(initial_data["world_demand"], initial_data["cycles"]["total"])
    create_transactions(initial_data["initial_balance"], users)
    create_thetas(users, initial_data["markets"])
    create_stocks(initial_data["initial_stocks_price"], users)
    # tables without initial data
    op.create_table(
        "production",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id"), nullable=False),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("market", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )
    op.create_table(
        "supplies",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts_start", sa.DateTime),
        sa.Column("ts_finish", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id"), nullable=False),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("market", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("delivered", sa.Integer),
    )
    op.create_table(
        "fee_modificators",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("fee", AutoString),
        sa.Column("coeff", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user", "fee"),
    )
    op.create_table(
        "bulletins",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
    )
    balances_view_sql = """
        CREATE VIEW balances AS
        SELECT
            ts.cycle,
            ts.user,
            SUM(ts.delta) OVER (PARTITION BY ts.user ORDER BY ts.cycle) AS balance
        FROM (
            SELECT t.cycle, t.user, SUM(t.amount) AS delta
            FROM transactions t
            GROUP BY t.cycle, t.user
        ) AS ts
    """
    warehouses_view_sql = """
        CREATE VIEW warehouses AS
        SELECT w.cycle, w.user, w.market, SUM(w.delta) OVER (PARTITION BY w.user, w.market ORDER BY w.cycle) AS quantity
        FROM (
            SELECT ps.cycle, ps.user, ps.market, SUM(ps.quantity) AS delta
                FROM (
                    SELECT p.cycle, p.user, p.market, p.quantity AS quantity
                    FROM production p
                    UNION ALL
                    SELECT s.cycle, s.user, s.market, -COALESCE(NULLIF(s.delivered, 0), s.quantity) AS quantity
                    FROM supplies s
                ) AS ps
            GROUP BY ps.cycle, ps.user, ps.market
        ) AS w
    """
    op.execute(balances_view_sql)
    op.execute(warehouses_view_sql)
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


def create_sync_status(users: list[dict[str, int | str]]) -> None:
    sync_table = op.create_table(
        "sync_status",
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("synced", sa.Boolean, nullable=False),
    )
    if sync_table is not None:
        initial_sync = [{"user": user["id"], "synced": False} for user in users if user["role"] == "player"]
        op.bulk_insert(sync_table, initial_sync)
    else:
        raise RuntimeError("Failed to create cycle sync table")


def create_npcs(npcs: list[dict[str, int]]) -> None:
    # npcs table (user_id, ring)
    npcs_table = op.create_table(
        "npcs",
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("ring", sa.Integer, nullable=False),
    )
    if npcs_table is not None:
        op.bulk_insert(npcs_table, npcs)
    else:
        raise RuntimeError("Failed to create NPCs table")


def create_cycles(
    total: int,
    fees: dict[str, tuple[float, float]],
    constants: dict[str, int | float],
) -> None:
    # game cycles table
    cycles_table = op.create_table(
        "cycles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts_start", sa.DateTime),
        sa.Column("ts_finish", sa.DateTime),
        sa.Column("alpha", sa.Float, nullable=False),
        sa.Column("beta", sa.Float, nullable=False),
        sa.Column("gamma", sa.Float, nullable=False),
        sa.Column("tau_s", sa.Integer, nullable=False),
        sa.Column("coeff_h", sa.Integer, nullable=False),
        sa.Column("coeff_k", sa.Integer, nullable=False),
        sa.Column("coeff_l", sa.Integer, nullable=False),
        sa.Column("overdraft_rate", sa.Float, nullable=False),
    )
    if cycles_table is not None:
        cycles: list[dict[str, int | float]] = [
            {
                "id": cycle + 1,
                **{fee: round(init_fee * mult ** cycle, 2) for fee, (init_fee, mult) in fees.items()},
                **constants,
            }
            for cycle in range(total)
        ]
        op.bulk_insert(cycles_table, cycles)
    else:
        raise RuntimeError("Failed to create cycles table")


def create_markets(markets: list[dict[str, int | str]]) -> None:
    # markets table (graph nodes)
    markets_table = op.create_table(
        "markets",
        sa.Column("id", sa.Integer, autoincrement=False, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("ring", sa.Integer, nullable=False),  # 2, 1, 0
        sa.Column("home_user", sa.Integer, sa.ForeignKey("users.id")),
    )
    if markets_table is not None:
        op.bulk_insert(markets_table, markets)
    else:
        raise RuntimeError("Failed to create markets table")


def create_market_connections(market_connections: list[dict[str, int]]) -> None:
    # markets connections table (graph edges list)
    market_connections_table = op.create_table(
        "market_connections",
        sa.Column("source", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("target", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
    )
    if market_connections_table is not None:
        op.bulk_insert(market_connections_table, market_connections)
    else:
        raise RuntimeError("Failed to create market connections table")


def create_market_prices(market_prices: list[dict[str, int | float]]) -> None:
    market_prices_table = op.create_table(
        "market_prices",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("market", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("buy", sa.Float, nullable=False),
        sa.Column("sell", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "market"),
    )
    if market_prices_table is not None:
        op.bulk_insert(market_prices_table, market_prices)
    else:
        raise RuntimeError("Failed to create market prices table")


def create_market_shares(
    users: list[dict[str, int | str]],
    markets: list[dict[str, int | str]],
) -> None:
    market_shares_table = op.create_table(
        "market_shares",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("share", sa.Float, nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("unlocked", sa.Boolean, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user", "market"),
    )
    if market_shares_table is not None:
        shares = [
            {
                "cycle": 1,
                "user": user["id"],
                "market": market["id"],
                "share": 0,
                "position": 0,
                "unlocked": market["home_user"] == user["id"],
            }
            for user, market in itertools.product(users, markets)
            if user["role"] == "player"
        ]
        op.bulk_insert(market_shares_table, shares)
    else:
        raise RuntimeError("Failed to create market shares table")


def create_world_demand(world_demand: dict[int, list[int]], n_cycles: int) -> None:
    world_demand_table = op.create_table(
        "world_demand",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("ring", sa.Integer),
        sa.Column("demand_pm", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "ring"),
    )
    if world_demand_table is not None:
        demand_records = [
            {"cycle": cycle, "ring": ring, "demand_pm": world_demand[ring][cycle - 1]}
            for cycle, ring in itertools.product(range(1, n_cycles + 1), range(3))
        ]
        op.bulk_insert(world_demand_table, demand_records)
    else:
        raise RuntimeError("Failed to create world demand table")


def create_transactions(amount: float, users: list[dict[str, int | str]]) -> None:
    transactions_table = op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id"), nullable=False),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
    )
    if transactions_table is not None:
        transactions = [
            {
                "ts": datetime.now(),
                "cycle": 1,
                "user": user["id"],
                "amount": amount,
                "description": "Initial balance",
            }
            for user in users
            if user["role"] == "player"
        ]
        op.bulk_insert(transactions_table, transactions)
    else:
        raise RuntimeError("Failed to create transactions table")


def create_thetas(
    users: list[dict[str, int | str]],
    markets: list[dict[str, int | str]],
) -> None:
    thetas_table = op.create_table(
        "thetas",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("theta", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user", "market"),
    )
    if thetas_table is not None:
        thetas = [
            {"cycle": 1, "user": user["id"], "market": market["id"], "theta": 0}
            for user, market in itertools.product(users, markets)
            if user["role"] == "player"
        ]
        op.bulk_insert(thetas_table, thetas)
    else:
        raise RuntimeError("Failed to create thetas table")


def create_stocks(initial_price: float, users: list[dict[str, int | str]]) -> None:
    stocks_table = op.create_table(
        "stocks",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.id")),
        sa.Column("user", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("price", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user"),
    )
    if stocks_table is not None:
        stocks = [
            {
                "cycle": 1,
                "user": user["id"],
                "price": initial_price,
            }
            for user in users
            if user["role"] in {"player", "npc"}
        ]
        op.bulk_insert(stocks_table, stocks)
    else:
        raise RuntimeError("Failed to create stocks table")


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    views = ("warehouses", "balances")
    tables = (
        "bulletins",
        "fee_modificators",
        "supplies",
        "production",
        "stocks",
        "thetas",
        "transactions",
        "world_demand",
        "market_shares",
        "market_prices",
        "market_connections",
        "markets",
        "cycles",
        "sync_status",
        "npcs",
        "users",
    )
    for view in views:
        op.execute(f"DROP VIEW {view};")
    for table in tables:
        op.drop_table(table)
    # ### end Alembic commands ###
