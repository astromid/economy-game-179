"""Created all necessary tables.

Revision ID: 2
Revises: 1
Create Date: 2022-10-07 17:32:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "2"
down_revision = "1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(  # users table (root, players, NPCs)
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("login", sa.Text),
        sa.Column("password", sa.Text),
    )
    op.create_table(  # game cycles table
        "cycles",
        sa.Column("cycle", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("started", sa.DateTime),
        sa.Column("finished", sa.DateTime),
        sa.Column("alpha", sa.Float, nullable=False),
        sa.Column("beta", sa.Float, nullable=False),
        sa.Column("gamma", sa.Float, nullable=False),
        sa.Column("tau_s", sa.Integer, nullable=False),
    )
    op.create_table(  # markets graph table (as an adjacency list)
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
    op.create_table(
        "world_demand",
        sa.Column("cycle", sa.Integer, primary_key=True),
        sa.Column("ring0", sa.Integer, nullable=False),
        sa.Column("ring1", sa.Integer, nullable=False),
        sa.Column("ring2", sa.Integer, nullable=False),
    )
    op.create_table(
        "prices",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("buy", sa.Float, nullable=False),
        sa.Column("sell", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "market_id"),
    )
    op.create_table(
        "stocks",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("price", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    op.create_table(  # money transactions table
        "transactions",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("timestamp", sa.DateTime, default=mysql.CURRENT_TIMESTAMP),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text),
    )
    op.create_table(
        "balances",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id"),
    )
    op.create_table(
        "logistics_operations",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("description", sa.Text),
    )
    op.create_table(
        "products",
        sa.Column("cycle", sa.Integer, sa.ForeignKey("cycles.cycle")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id")),
        sa.Column("storage", sa.Integer, nullable=False),
        sa.Column("theta", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("cycle", "user_id", "market_id"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("cycles")
    op.drop_table("markets")
    op.drop_table("world_demand")
    op.drop_table("prices")
    op.drop_table("stocks")
    op.drop_table("transactions")
    op.drop_table("balances")
    op.drop_table("logistics_operations")
    op.drop_table("products")
