"""Modificators API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class FeeModificator(BaseModel):
    """Modificator model."""

    cycle: int
    user: int
    fee: str
    coeff: float


class ModificatorAPI:
    """Modificators API."""

    _api_url = settings.backend_url / "modificators"
    _list_url = str(_api_url / "list")
    _list_all_url = str(_api_url / "list" / "all")
    _new_url = str(_api_url / "new")

    @classmethod
    def get_user_modificators(cls) -> list[FeeModificator]:
        """Get current user modificators.

        Returns:
            list[Modificator]: current user modificators.
        """
        response = httpx.get(cls._list_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[FeeModificator], response.json())

    @classmethod
    def get_modificators(cls) -> list[FeeModificator]:
        """Get all users modificators.

        Returns:
            list[Modificator]: all users modificators.
        """
        response = httpx.get(cls._list_all_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[FeeModificator], response.json())

    @classmethod
    def new(cls, cycle: int, user: int, fee: str, coeff: float) -> None:
        """Create new fee modificator.

        Args:
            cycle (int): target cycle.
            user (int): target user id.
            fee (str): fee name.
            coeff (float): fee coefficient.
        """
        new_mod = {"cycle": cycle, "user": user, "fee": fee, "coeff": coeff}
        response = httpx.post(cls._new_url, json=new_mod, headers=st.session_state.auth_header)
        response.raise_for_status()
