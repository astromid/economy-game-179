import httpx

from egame179_frontend.api.models import User
from egame179_frontend.settings import settings

AUTH_HEADER = "Bearer {token}"
TOKEN_URL = settings.backend_url / "token"  # noqa: S105
USERINFO_URL = settings.backend_url / "userinfo"


def get_auth_header(login: str, password: str) -> dict[str, str] | None:
    """Get authentification header for the given login and password.

    Args:
        login (str): user login.
        password (str): user password.

    Returns:
        dict[str, str] | None: auth header or None if login or password is incorrect.
    """
    response = httpx.post(str(TOKEN_URL), data={"username": login, "password": password})
    if response.status_code == httpx.codes.UNAUTHORIZED:
        return None
    token_data = response.json()
    return {"Authorization": AUTH_HEADER.format(token=token_data["access_token"])}


def get_user(auth_header: dict[str, str]) -> User | None:
    """Get authenticated user info.

    Args:
        auth_header (dict[str, str]): auth header.

    Returns:
        User | None: user info or None if auth header is incorrect.
    """
    response = httpx.get(str(USERINFO_URL), headers=auth_header)
    if response.status_code == httpx.codes.UNAUTHORIZED:
        return None
    return User.parse_obj(response.json())
