from fastapi import APIRouter, Depends
from pydantic import BaseModel

from egame179_backend.db.stocks import Stock, StockDAO

router = APIRouter()


class StockPrice(BaseModel):
    """Stock model with only price."""

    cycle: int
    user: int
    price: float


@router.get("/list/all", response_model=list[StockPrice])
async def get_stocks(dao: StockDAO = Depends()) -> list[Stock]:
    """Get stocks.

    Args:
        dao (StockDAO): stocks table data access object.

    Returns:
        list[Stock]: stocks history.
    """
    return await dao.select()
