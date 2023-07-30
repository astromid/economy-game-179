from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.transaction import Transaction, TransactionDAO
from egame179_backend.db.user import User

router = APIRouter()


@router.get("/list")
async def get_user_transactions(
    user: User = Depends(get_current_user),
    dao: TransactionDAO = Depends(),
) -> list[Transaction]:
    """Get transactions history for user.

    Args:
        user (User): authenticated user data.
        dao (TransactionDAO): transactions table data access object.

    Returns:
        list[Transaction]: transactions history for user.
    """
    return await dao.select(user.id)


@router.get("/list/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_transactions(dao: TransactionDAO = Depends()) -> list[Transaction]:
    """Get transactions history.

    Args:
        dao (TransactionDAO): transactions table data access object.

    Returns:
        list[Transaction]: transactions history.
    """
    return await dao.select()
