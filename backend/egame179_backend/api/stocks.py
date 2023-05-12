from fastapi import APIRouter, Depends
from pydantic import BaseModel

from egame179_backend.db.stocks import Stock, StockDAO

router = APIRouter()


class StockNoise(BaseModel):
    """Stock model with only noised price."""

    cycle: int
    user_id: int
    price_noise: float


@router.get("/all", response_model=list[StockNoise])
async def get_stocks(dao: StockDAO = Depends()) -> list[Stock]:
    """Get stocks.

    Args:
        dao (StockDAO): stocks table data access object.

    Returns:
        list[Stock]: stocks history.
    """
    return await dao.get()
