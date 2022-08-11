"""Input JSON models with game state from backend."""
from pydantic import BaseModel


class GameState(BaseModel):
    """Shared state of the game."""

    cycle: int
    player_stocks: dict[str, list[float]]
    npc_stocks: dict[str, list[float]]
    markets_buy: dict[str, list[float]]
    markets_sell: dict[str, list[float]]
    markets_top: dict[str, dict[str, float | None]]


class PlayerState(GameState):
    """Game state from current player POV."""

    balance: list[float]
    thetas: dict[str, float]
    storage: dict[str, float]


class MasterState(GameState):
    """Game state from the game master POV."""

    god_mode: bool = True
    players: dict[str, PlayerState]
