from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel

from egame179_frontend.settings import settings


class Cycle(BaseModel):
    """Cycle model."""

    cycle: int
    started: datetime | None
    finished: datetime | None


class CycleAPI:
    """Cycle API."""

    current_cycle_url = str(settings.backend_url / "cycle" / "current")
    finish_cycle_url = str(settings.backend_url / "cycle" / "finish")
    start_cycle_url = str(settings.backend_url / "cycle" / "new")

    @classmethod
    def get_cycle(cls) -> Cycle:
        """Get current cycle.

        Returns:
            Cycle: current cycle info.
        """
        response = httpx.get(cls.current_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return Cycle.parse_obj(response.json())

    @classmethod
    def finish_cycle(cls) -> None:
        """Finish current cycle."""
        response = httpx.post(cls.finish_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()

    @classmethod
    def start_cycle(cls) -> None:
        """Start new cycle."""
        response = httpx.post(cls.start_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()
