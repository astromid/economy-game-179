"""Connector with the backend API."""
from pydantic import BaseModel


class StockRecord(BaseModel):
    """Stock record."""

    ticket: str
    cycle: int
    price: float


class SharedState(BaseModel):
    """Shared state of the game."""

    cycle: int
    stocks: list[StockRecord]
    resources: dict[str, dict[str, float]]


class PlayerState(SharedState):
    """Game state from current player POV."""

    balance: float
    balance_delta: float


class GameState(SharedState):
    """Game state from the game master POV."""

    pass
