"""Cycles API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Cycle(BaseModel):
    """Cycle model."""

    cycle: int
    ts_start: datetime | None
    ts_finish: datetime | None


class CycleParams(BaseModel):
    """Cycle parameters model."""

    alpha: float
    beta: float
    gamma: float
    tau_s: int


class DemandFactor(BaseModel):
    """Demand factors for each market."""

    market_id: int
    factor: float


class CycleAPI:
    """Cycle API."""

    _api_url = settings.backend_url / "cycle"

    _get_cycle_url = str(_api_url / "current")
    _create_cycle_url = str(_api_url / "new")
    _start_cycle_url = str(_api_url / "start")
    _finish_cycle_url = str(_api_url / "finish")
    _cycle_params_url = str(_api_url / "params")
    _demand_factors_url = str(_api_url / "demand_factors")

    @classmethod
    def get_cycle(cls) -> Cycle:
        """Get current cycle.

        Returns:
            Cycle: current cycle info.
        """
        response = httpx.get(cls._get_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return Cycle.parse_obj(response.json())

    @classmethod
    def create_cycle(cls) -> None:
        """Create new cycle."""
        response = httpx.get(cls._create_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()

    @classmethod
    def start_cycle(cls) -> None:
        """Start new cycle."""
        response = httpx.get(cls._start_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()

    @classmethod
    def finish_cycle(cls) -> None:
        """Finish current cycle."""
        response = httpx.get(cls._finish_cycle_url, headers=st.session_state.auth_header)
        response.raise_for_status()

    @classmethod
    def get_cycle_parameters(cls) -> CycleParams:
        """Get current cycle parameters.

        Returns:
            CycleParams: current cycle parameters.
        """
        response = httpx.get(cls._cycle_params_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return CycleParams.parse_obj(response.json())

    @classmethod
    def get_demand_factors(cls) -> list[DemandFactor]:
        """Get current market demand factors.

        Returns:
            list[DemandFactor]: current cycle demand factors.
        """
        response = httpx.get(cls._demand_factors_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[DemandFactor], response.json())
