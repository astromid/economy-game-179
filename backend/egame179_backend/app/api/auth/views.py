from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt

from egame179_backend.app.api.auth.schema import Token, UserInfo
from egame179_backend.db.dao.users import UserDAO
from egame179_backend.db.models import User
from egame179_backend.settings import settings

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "root": "Read / write admin data",
        "editor": "Read / write news data",
        "news": "Read news data",
        "player": "Read / write player data",
    },
)


def create_access_token(payload: dict[str, Any]) -> str:
    """Create an JWT access token.

    Args:
        payload (dict[str, Any]): token payload.

    Returns:
        str: encoded token
    """
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**payload, "exp": expire}, settings.jwt_secret, algorithm=ALGORITHM)


async def get_current_user(  # noqa: WPS238, C901
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    user_dao: UserDAO = Depends(),
) -> User:
    """Get current authorized user.

    Args:
        security_scopes (SecurityScopes): fastAPI security scopes.
        token (str): authorization token.
        user_dao (UserDAO): DAO for users table.

    Raises:
        credentials_exception: JWTError
        credentials_exception: Token is invalid
        credentials_exception: User not found
        HTTPException: User have no permissions

    Returns:
        User: user information from database.
    """
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope='{security_scopes.scope_str}'"
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc

    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = await user_dao.get_user(name=username)
    if user is None:
        raise credentials_exception

    token_scopes = payload.get("scopes", [])
    if set(token_scopes) != set(security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user


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
