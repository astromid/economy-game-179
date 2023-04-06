"""Backend API models."""
from pydantic import BaseModel


class GameParams(BaseModel):
    """Game parameters."""

    tau: int
    alpha: float
    beta: float
    gamma: float


class MarketState(BaseModel):
    """Market state."""

    adjacency: list[str]
    buy: list[float]
    sell: list[float]


class GameState(BaseModel):
    """Shared state of the game."""

    cycle: int
    game_params: GameParams
    markets: dict[str, MarketState]
    stocks: dict[str, dict[str, list[float]]]


class Transaction(BaseModel):
    """Transaction model."""

    cycle: int
    amount: float
    type_: str
    description: str | None


class PlayerMarketInfo(BaseModel):
    """Player market info."""

    theta: float
    storage: int
    top: dict[str, float | None]


class PlayerInfo(BaseModel):
    """Player state."""

    name: str
    home: str
    balances: list[float]
    active_markets: list[str]
    products: dict[str, PlayerMarketInfo]
    transactions: list[Transaction]


class PlayerState(GameState):
    """Game state from current player POV."""

    player: PlayerInfo
