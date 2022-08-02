"""Connector with the backend API."""
from pydantic import BaseModel


class PlayerState(BaseModel):
    """Game state from current player POV."""

    cycle: int
    stocks: list[dict[str, str | int | float]]
    resources: dict[str, dict[str, float]]


class GameState(BaseModel):
    """Game state from the game master POV."""

    cycle: str
