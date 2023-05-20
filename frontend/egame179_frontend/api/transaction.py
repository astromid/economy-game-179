"""Transactions API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Transaction(BaseModel):
    """Transaction model."""

    id: int
    ts: datetime
    cycle: int
    user: int
    amount: float
    description: str


class TransactionAPI:
    """Transaction API."""

    _api_url = settings.backend_url / "transaction"
    _user_transactions_url = str(_api_url / "list")
    _transactions_url = str(_api_url / "list/all")

    @classmethod
    def get_user_transactions(cls) -> list[Transaction]:
        """Get current user transactions.

        Returns:
            list[Transaction]: current user transactions.
        """
        response = httpx.get(cls._user_transactions_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Transaction], response.json())

    @classmethod
    def get_transactions(cls) -> list[Transaction]:
        """Get transactions.

        Returns:
            list[Transaction]: current user transactions.
        """
        response = httpx.get(cls._transactions_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Transaction], response.json())
