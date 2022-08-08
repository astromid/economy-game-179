"""Input JSON models with game state from backend."""
from pydantic import BaseModel


class MarketStatus(BaseModel):
    """Market status (shared state)."""

    buy: list[float]
    sell: list[float]
    top: dict[str, float | None]


class GameState(BaseModel):
    """Shared state of the game."""

    cycle: int
    player_stocks: dict[str, list[float]]
    npc_stocks: dict[str, list[float]]
    markets: dict[str, MarketStatus]


class PlayerState(GameState):
    """Game state from current player POV."""

    balance: list[float]
    theta: dict[str, float]
    storage: dict[str, float]


class MasterState(GameState):
    """Game state from the game master POV."""

    god_mode: bool = True
