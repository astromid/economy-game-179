from fastapi import APIRouter, Depends

from egame179_backend.db.price import Price, PriceDAO

router = APIRouter()


@router.get("/all")
async def get_prices(dao: PriceDAO = Depends()) -> list[Price]:
    """Get all markets prices.

    Args:
        dao (PriceDAO): prices table data access object.

    Returns:
        list[Prices]: list of market prices.
    """
    return await dao.get()
