import httpx
from streamlit_server_state import server_state

from egame179_frontend.api.models import User
from egame179_frontend.settings import Settings


def auth_request(login: str, password: str) -> User | None:
    settings: Settings = server_state.settings
    response = httpx.post(
        str(settings.backend_url / "auth" / "auth"),
        json={"login": login, "password": password},
    )
    if response.status_code == httpx.codes.UNAUTHORIZED:
        return None
    return User.parse_obj(response.json())
