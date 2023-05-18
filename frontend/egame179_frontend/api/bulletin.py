"""Bulletins API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Bulletin(BaseModel):
    """Bulletin model."""

    id: int
    ts: datetime
    cycle: int
    text: str


class BulletinAPI:
    """Bulletin API."""

    _list_url = str(settings.backend_url / "bulletin/list")

    @classmethod
    def get_bulletins(cls) -> list[Bulletin]:
        """Get current cycle bulletins.

        Returns:
            list[Bulletin]: current cycle bulletins.
        """
        response = httpx.get(cls._list_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Bulletin], response.json())
