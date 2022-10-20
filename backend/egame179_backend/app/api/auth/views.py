from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from egame179_backend.app.api.auth.dependencies import ALGORITHM, get_current_user
from egame179_backend.app.api.auth.schema import Token, UserInfo
from egame179_backend.db.dao.users import UserDAO
from egame179_backend.db.models import User
from egame179_backend.settings import settings

TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()


def create_access_token(payload: dict[str, Any]) -> str:
    """Create an JWT access token.

    Args:
        payload (dict[str, Any]): token payload.

    Returns:
        str: encoded token
    """
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**payload, "exp": expire}, settings.jwt_secret, algorithm=ALGORITHM)


@router.post("/token")
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_dao: UserDAO = Depends(),
) -> Token:
    """Get user access token.

    Args:
        form_data (OAuth2PasswordRequestForm): login and password from form.
        user_dao (UserDAO): user table data access object.

    Raises:
        HTTPException: incorrect username or password.

    Returns:
        Token: generated token.
    """
    user = await user_dao.check_credentials(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.name, "scopes": [user.role]})
    return Token(access_token=access_token, token_type="bearer")  # noqa: S106


@router.get("/userinfo", response_model=UserInfo)
async def get_user_info(user: User = Depends(get_current_user)) -> User:
    """Get authorized user info.

    Args:
        user (User): authenticated user data.

    Returns:
        User: UserInfo response model.
    """
    return user
