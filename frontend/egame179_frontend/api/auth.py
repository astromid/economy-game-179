import httpx

from egame179_frontend.api.models import User
from egame179_frontend.settings import settings


class AuthAPI:
    """Authentication API."""

    token_url = str(settings.backend_url / "token")
    userinfo_url = str(settings.backend_url / "userinfo")

    @classmethod
    def get_auth_header(cls, login: str, password: str) -> dict[str, str] | None:
        """Get authentication header for the given login and password.

        Args:
            login (str): user login.
            password (str): user password.

        Returns:
            dict[str, str] | None: auth header or None if login or password is incorrect.
        """
        response = httpx.post(cls.token_url, data={"username": login, "password": password})
        if response.status_code == httpx.codes.UNAUTHORIZED:
            return None
        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}

    @classmethod
    def get_user(cls, auth_header: dict[str, str]) -> User | None:
        """Get authenticated user info.

        Args:
            auth_header (dict[str, str]): auth header.

        Returns:
            User | None: user info or None if auth header is incorrect.
        """
        response = httpx.get(cls.userinfo_url, headers=auth_header)
        if response.status_code == httpx.codes.UNAUTHORIZED:
            return None
        return User.parse_obj(response.json())
