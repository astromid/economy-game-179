from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Users table."""

    __tablename__ = "users"  # type: ignore

    id: int = Field(primary_key=True)
    role: str
    name: str
    login: str | None
    password: str | None


class Market(SQLModel, table=True):
    """Markets table."""

    __tablename__ = "markets"  # type: ignore

    id: int = Field(primary_key=True)
    name: str
    ring: int
    link1: int
    link2: int
    link3: int
    link4: int | None
    link5: int | None


class UnlockedMarket(SQLModel, table=True):
    """Unlocked markets table."""

    __tablename__ = "unlocked_markets"  # type: ignore

    user_id: int = Field(primary_key=True)
    market_id: int = Field(primary_key=True)
    protected: bool


class Cycle(SQLModel, table=True):
    """Cycles table."""

    __tablename__ = "cycles"  # type: ignore

    cycle: int | None = Field(default=None, primary_key=True)
    started: datetime | None = Field(default_factory=datetime.now)
    finished: datetime | None = None
