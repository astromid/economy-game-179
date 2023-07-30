from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt

from egame179_backend.db.user import User, UserDAO
from egame179_backend.settings import settings

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "root": "Read / write admin data",
        "editor": "Read / write news data",
        "news": "Read news data",
        "player": "Read / write player data",
    },
)


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
    try:  # check token decoding
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc
    # check token permissions
    token_scopes = set(payload.get("scopes", []))
    if not token_scopes.issuperset(security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    user: User | None = None
    # check valid username
    username: str | None = payload.get("sub")
    if username is not None:
        user = await user_dao.get_by_name(username)  # check user in database
    if user is None:
        raise credentials_exception
    return user
