from fastapi import APIRouter, Depends, Security

from egame179_backend.app.api.auth.dependencies import get_current_user
from egame179_backend.db.dao.balances import BalanceDAO
from egame179_backend.db.models import Balance, User

router = APIRouter()


@router.get("/user", dependencies=[Security(get_current_user, scopes=["player"])])
async def get_user_balances(
    user: User = Depends(get_current_user),
    balance_dao: BalanceDAO = Depends(),
) -> list[Balance]:
    """Get balances history for user.

    Args:
        user (User): authenticated user data.
        balance_dao (BalanceDAO): balances table data access object.

    Returns:
        list[Balance]: balances history for user.
    """
    return await balance_dao.get_user_balances(user.id)


@router.get("/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_all_balances(balance_dao: BalanceDAO = Depends()) -> list[Balance]:
    """Get balances history for all users.

    Args:
        balance_dao (BalanceDAO): balances table data access object.

    Returns:
        list[Balance]: balances history for all users.
    """
    return await balance_dao.get_all_balances()
