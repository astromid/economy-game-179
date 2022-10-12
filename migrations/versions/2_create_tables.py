"""Created all necessary tables & fill them with initial data.

Revision ID: 2
Revises: 1
Create Date: 2022-10-07 17:32:00.000000

"""
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
    create_users(initial_data["users"])
    create_cycles()
    # op.create_table(
    #     "cycle_parameters",
    #     sa.Column("cycle", sa.Integer, primary_key=True),
    #     sa.Column("alpha", sa.Float, nullable=False),
    #     sa.Column("beta", sa.Float, nullable=False),
    #     sa.Column("gamma", sa.Float, nullable=False),
    #     sa.Column("tau_s", sa.Integer, nullable=False),
    #     sa.Column("demand_ring0", sa.Integer, nullable=False),
    #     sa.Column("demand_ring1", sa.Integer, nullable=False),
    #     sa.Column("demand_ring2", sa.Integer, nullable=False),
    # )
    # op.create_table(  # markets graph table (as an adjacency list)
    #     "markets",
    #     sa.Column("id", sa.Integer, primary_key=True),
    #     sa.Column("name", sa.Text, nullable=False),
    #     sa.Column("ring", sa.Integer, nullable=False),  # 2, 1, 0
    #     sa.Column("link1", sa.Integer),
    #     sa.Column("link2", sa.Integer),
    #     sa.Column("link3", sa.Integer),
    #     sa.Column("link4", sa.Integer),
    #     sa.Column("link5", sa.Integer),
    # )
    # op.create_table(
    #     "prices",
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
    #     sa.Column("buy", sa.Float, nullable=False),
    #     sa.Column("sell", sa.Float, nullable=False),
    #     sa.PrimaryKeyConstraint("cycle", "market_id"),
    # )
    # op.create_table(
    #     "stocks",
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("price", sa.Float, nullable=False),
    #     sa.PrimaryKeyConstraint("cycle", "user_id"),
    # )
    # op.create_table(  # money transactions table
    #     "transactions",
    #     sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
    #     sa.Column("timestamp", sa.DateTime),
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("amount", sa.Float, nullable=False),
    #     sa.Column("description", sa.Text),
    # )
    # op.create_table(
    #     "balances",
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("amount", sa.Float, nullable=False),
    #     sa.PrimaryKeyConstraint("cycle", "user_id"),
    # )
    # op.create_table(
    #     "logistics_operations",
    #     sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
    #     sa.Column("timestamp", sa.DateTime),
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
    #     sa.Column("amount", sa.Integer, nullable=False),
    #     sa.Column("description", sa.Text),
    # )
    # op.create_table(
    #     "products",
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
    #     sa.Column("storage", sa.Integer, nullable=False),
    #     sa.Column("theta", sa.Float, nullable=False),
    #     sa.PrimaryKeyConstraint("cycle", "user_id", "market_id"),
    # )
    # op.create_table(
    #     "player_modificators",
    #     sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    #     sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
    #     sa.Column("parameter", sa.Text, nullable=False),
    #     sa.Column("value", sa.Float, nullable=False),
    #     sa.PrimaryKeyConstraint("cycle", "user_id", "market_id", "parameter"),
    # )


def create_users(users: list[dict[str, str]]) -> None:
    users_table = op.create_table(  # users table (root, players, NPCs)
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("login", sa.Text),
        sa.Column("password", sa.Text),
    )
    if users_table is not None:
        op.bulk_insert(users_table, users)

def create_cycles() -> None:
    cycles_table = op.create_table(  # game cycles table
        "cycles",
        sa.Column("cycle", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("started", sa.DateTime),
        sa.Column("finished", sa.DateTime),
    )
    if cycles_table is not None:
        op.bulk_insert(cycles_table, [{"cycle": 0}])


def downgrade() -> None:
    tables = (
        # "player_modificators",
        # "products",
        # "logistics_operations",
        # "balances",
        # "transactions",
        # "stocks",
        # "prices",
        # "markets",
        # "cycle_parameters",
        "cycles",
        "users",
    )
    for table in tables:
        op.drop_table(table)
