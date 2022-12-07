import time
from dataclasses import dataclass

from streamlit_server_state import server_state, server_state_lock

from egame179_frontend import api as egame179_api
from egame179_frontend.api import models as api_models
from egame179_frontend.fetch_ui import fetch_spinner


@dataclass
class SharedGameState:
    """Shared game state for all players."""

    synced: bool
    cycle: api_models.Cycle


def init_server_state() -> None:
    """Initialize server state (from root)."""
    with server_state_lock["game"]:
        if "game" not in server_state:
            server_state["game"] = None


def fetch_shared_state() -> None:
    """Fetch shared state from server."""
    state = SharedGameState(
        synced=True,
        cycle=fetch_current_cycle(),
    )
    with server_state_lock["game"]:
        server_state["game"] = state


@fetch_spinner(stage=1, total=4)
def fetch_current_cycle() -> egame179_api.models.Cycle:
    """Fetch current cycle from server.

    Returns:
        egame179_api.models.Cycle: current cycle.
    """
    time.sleep(5)  # !DEBUG
    return egame179_api.CycleAPI.get_current_cycle()
