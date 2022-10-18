from fastapi import APIRouter, Body, Depends, HTTPException, status

from egame179_backend.app.api.auth.schema import UserOut
from egame179_backend.db.dao.users import UserDAO
from egame179_backend.db.models import User

router = APIRouter()


@router.post("/auth", response_model=UserOut)
async def auth(login: str = Body(), password: str = Body(), user_dao: UserDAO = Depends()) -> User:
    """Perform user authentication.

    Args:
        login (str): user login.
        password (str): user password.
        user_dao (UserDAO): DAO for users table.

    Raises:
        HTTPException: Incorrect login or password.

    Returns:
        User: user data (without sensitive information).
    """
    user = await user_dao.auth(login, password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return user
