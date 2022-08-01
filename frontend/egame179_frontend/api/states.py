"""Connector with the backend API."""
from dataclasses import dataclass

import pandas as pd


@dataclass
class PlayerState:
    """Game state from current player POV."""

    cycle: int
    stocks: pd.DataFrame


@dataclass
class GameState:
    """Game state from the game master POV."""

    cycle: str
