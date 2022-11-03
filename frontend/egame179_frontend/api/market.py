import httpx
import streamlit as st

from egame179_frontend.api.models import Market
from egame179_frontend.settings import settings


class MarketAPI:
    """Market API."""
