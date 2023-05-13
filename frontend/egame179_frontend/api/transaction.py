"""Transactions API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Transaction(BaseModel):
    """Transaction model."""

    ts: datetime
    cycle: int
    user_id: int
    amount: float
    description: str
    items: int | None = None
    market_id: int | None = None


class TransactionAPI:
    """Transaction API."""

    _user_transactions_url = str(settings.backend_url / "transaction" / "user")

    @classmethod
    def get_user_transactions(cls) -> list[Transaction]:
        """Get current user transactions.

        Returns:
            list[Transaction]: current user transactions.
        """
        response = httpx.get(cls._user_transactions_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Transaction], response.json())
