from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.market import Market, MarketDAO, UnlockedMarket, UnlockedMarketDAO
from egame179_backend.db.user import User

router = APIRouter()


@router.get("/all", dependencies=[Security(get_current_user)])
async def get_all_markets(dao: MarketDAO = Depends()) -> list[Market]:
    """Get all markets graph nodes.

    Args:
        dao (MarketDAO): markets table data access object.

    Returns:
        list[Markets]: list of markets nodes.
    """
    return await dao.get_markets()


@router.get("/unlocked/user")
async def get_user_unlocked_markets(
    dao: UnlockedMarketDAO = Depends(),
    user: User = Depends(get_current_user),
) -> list[UnlockedMarket]:
    """Get unlocked markets for current user.

    Args:
        dao (UnlockedMarketDAO): unlocked markets table data access object.
        user (User): current user.

    Returns:
        list[UnlockedMarkets]: list of markets nodes.
    """
    return await dao.get_user_unlocked_markets(user.id)


@router.get("/unlocked/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_unlocked_markets(dao: UnlockedMarketDAO = Depends()) -> list[UnlockedMarket]:
    """Get unlocked markets for all users.

    Args:
        dao (UnlockedMarketDAO): unlocked markets table data access object.

    Returns:
        list[UnlockedMarkets]: list of markets nodes.
    """
    return await dao.get_all_unlocked_markets()
