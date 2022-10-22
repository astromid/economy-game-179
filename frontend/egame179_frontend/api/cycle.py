import httpx
import streamlit as st

from egame179_frontend.api.models import Cycle
from egame179_frontend.settings import settings

CURRENT_CYCLE_URL = settings.backend_url / "cycle" / "current"


def get_current_cycle() -> Cycle:
    """Get current cycle.

    Returns:
        Cycle: current cycle info.
    """
    response = httpx.get(str(CURRENT_CYCLE_URL), headers=st.session_state.auth_header)
    response.raise_for_status()
    return Cycle.parse_obj(response.json())
