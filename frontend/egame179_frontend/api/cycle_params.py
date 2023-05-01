"""Cycle parameters API."""
import httpx
import streamlit as st
from pydantic import BaseModel

from egame179_frontend.settings import settings


class CycleParams(BaseModel):
    """Cycle parameters model."""

    alpha: float
    beta: float
    gamma: float
    tau_s: int


class CycleParamsAPI:
    """Cycle parameters API."""

    _cycle_params_url = str(settings.backend_url / "cycle_params")

    @classmethod
    def get_cycle_parameters(cls) -> CycleParams:
        """Get current cycle parameters.

        Returns:
            CycleParams: current cycle parameters.
        """
        response = httpx.get(cls._cycle_params_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return CycleParams.parse_obj(response.json())
