from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.price import Price, PriceDAO

router = APIRouter()


@router.get("/all", dependencies=[Security(get_current_user)])
async def get_all_markets(dao: PriceDAO = Depends()) -> list[Price]:
    """Get all markets prices.

    Args:
        dao (PriceDAO): prices table data access object.

    Returns:
        list[Prices]: list of market prices.
    """
    return await dao.get_prices()
