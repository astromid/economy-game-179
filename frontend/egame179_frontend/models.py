"""Input API models from backend."""
from datetime import datetime

from pydantic import BaseModel


class Roles:
    """User roles."""

    root = "root"
    editor = "editor"
    news = "news"
    player = "player"


class User(BaseModel):
    """User model."""

    id: int
    role: str
    name: str


class Market(BaseModel):
    """Market model."""

    id: int
    name: str
    ring: int
    link1: int
    link2: int
    link3: int
    link4: int | None
    link5: int | None


class Cycle(BaseModel):
    """Cycle model."""

    cycle: int
    started: datetime
    finished: datetime | None


# class GameParams(BaseModel):
#     """Game parameters."""

#     tau: int
#     alpha: float
#     beta: float
#     gamma: float


# class MarketState(BaseModel):
#     """Market state."""

#     adjacency: list[str]
#     buy: list[float]
#     sell: list[float]


# class GameState(BaseModel):
#     """Shared state of the game."""

#     cycle: int
#     game_params: GameParams
#     markets: dict[str, MarketState]
#     stocks: dict[str, dict[str, list[float]]]


# class Transaction(BaseModel):
#     """Transaction model."""

#     cycle: int
#     amount: float
#     type_: str
#     description: str | None


# class PlayerMarketInfo(BaseModel):
#     """Player market info."""

#     theta: float
#     storage: int
#     top: dict[str, float | None]


# class PlayerInfo(BaseModel):
#     """Player state."""

#     name: str
#     home: str
#     balances: list[float]
#     active_markets: list[str]
#     products: dict[str, PlayerMarketInfo]
#     transactions: list[Transaction]


# class PlayerState(GameState):
#     """Game state from current player POV."""

#     player: PlayerInfo


# class MasterState(GameState):
#     """Game state from the game master POV."""

#     players: dict[str, PlayerInfo]
