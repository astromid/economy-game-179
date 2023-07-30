from fastapi import APIRouter, Depends

from egame179_backend.db.market_price import MarketPrice, MarketPriceDAO

router = APIRouter()


@router.get("/market/prices")
async def get_market_prices(dao: MarketPriceDAO = Depends()) -> list[MarketPrice]:
    """Get all markets prices.

    Args:
        dao (MarketPriceDAO): prices table data access object.

    Returns:
        list[MarketPrices]: list of market prices.
    """
    return await dao.select()
