import math
from collections import defaultdict

from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import CycleDAO, WorldDemandDAO
from egame179_backend.db.market import Market, MarketDAO, MarketShare
from egame179_backend.db.user import User

router = APIRouter()


class MarketSharePlayer(BaseModel):
    """Market share with player visible info."""

    user: int
    market: int
    share: float | None = None
    position: int


class UnlockRequest(BaseModel):
    """Unlock market request."""

    cycle: int
    user: int
    market: int


@router.get("/nodes")
async def get_market_nodes(dao: MarketDAO = Depends()) -> list[Market]:
    """Get all markets graph nodes.

    Args:
        dao (MarketDAO): markets table data access object.

    Returns:
        list[Markets]: list of markets nodes.
    """
    return await dao.select_markets()


@router.get("/edges")
async def get_market_edges(dao: MarketDAO = Depends()) -> list[tuple[int, int]]:
    """Get all markets graph edges.

    Args:
        dao (MarketDAO): markets table data access object.

    Returns:
        list[tuple[int, int]]: list of market edges.
    """
    return await dao.select_connections()


@router.get("/unlocked")
async def get_user_unlocked_markets(
    dao: MarketDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    user: User = Depends(get_current_user),
) -> list[int]:
    """Get unlocked markets for current user.

    Args:
        dao (MarketDAO): markets table data access object.
        cycle_dao (CycleDAO): cycles table data access object.
        user (User): current user.

    Returns:
        list[int]: list of unlocked markets node ids.
    """
    current_cycle = await cycle_dao.get_current()
    shares = await dao.select_shares(cycle=current_cycle.id, user=user.id)
    return [share.market for share in shares if share.unlocked]


@router.get("/shares")
async def get_user_market_shares(
    user: User = Depends(get_current_user),
    dao: MarketDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
) -> list[MarketSharePlayer]:
    """Get player visible market shares.

    Args:
        user (User): authenticated user data.
        dao (MarketDAO): markets table data access object.
        cycle_dao (CycleDAO): cycle table data access object.

    Returns:
        list[MarketSharePlayer]: market shares visible for player.
    """
    current_cycle = await cycle_dao.get_current()
    markets = await dao.select_markets()
    prev_shares = await dao.select_shares(cycle=current_cycle.id - 1, nonzero=True)
    market_shares: dict[int, list[MarketShare]] = defaultdict(list)
    for share in prev_shares:
        market_shares[share.market].append(share)

    visible_shares = []
    for market in markets:
        pos_shares = {shr.position: (shr.user, shr.share) for shr in market_shares[market.id]}
        top2_users = [user for pos, (user, _) in pos_shares.items() if pos <= 2]
        if user.id not in top2_users:
            # filter information for non-owned markets (user not in top-2)
            visible_shares.extend(
                [
                    MarketSharePlayer(user=user, market=market.id, share=None, position=pos)
                    for pos, (user, _) in pos_shares.items()
                    if pos <= 2
                ],
            )
        else:
            visible_shares.extend(
                [
                    MarketSharePlayer(user=user, market=market.id, share=shr, position=pos)
                    for pos, (user, shr) in pos_shares.items()
                ],
            )
    return visible_shares


@router.get(
    "/shares/all",
    dependencies=[Security(get_current_user, scopes=["root"])],
    response_model=list[MarketSharePlayer],
)
async def get_market_shares(dao: MarketDAO = Depends(), cycle_dao: CycleDAO = Depends()) -> list[MarketShare]:
    """Get all market shares for previous cycle.

    Args:
        dao (MarketDAO): markets table data access object.
        cycle_dao (CycleDAO): cycle table data access object.

    Returns:
        list[MarketShare]: shares for all users.
    """
    current_cycle = await cycle_dao.get_current()
    return await dao.select_shares(cycle=current_cycle.id - 1, nonzero=True)


@router.post("/unlock", dependencies=[Security(get_current_user, scopes=["root"])])
async def unlock_market(unlock_request: UnlockRequest, dao: MarketDAO = Depends()) -> None:
    """Unlock market for user.

    Args:
        unlock_request (UnlockRequest): unlock request data.
        dao (MarketDAO): markets table data access object.
    """
    await dao.unlock_market(cycle=unlock_request.cycle, user=unlock_request.user, market=unlock_request.market)


@router.get("/demand_factors")
async def get_demand_factors(
    dao: WorldDemandDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
) -> dict[int, float]:
    """Get current market demand factors.

    Args:
        dao (WorldDemandDAO): world demand table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): market table data access object.

    Returns:
        dict[int, float]: demand factors for each market.
    """
    current_cycle = await cycle_dao.get_current()
    markets = await market_dao.select_markets()
    current_demand = await dao.select(cycle=current_cycle.id)
    initial_demand = await dao.select(cycle=1)
    factors: dict[int, float] = {}
    for market in markets:
        rel_d = current_demand[market.ring] / initial_demand[market.ring]
        if rel_d >= 1:
            factors[market.id] = math.log(rel_d) + 1
        else:
            factors[market.id] = math.sqrt(rel_d)
    return factors
