from pydantic import BaseModel


class AuthData(BaseModel):
    """Login & password."""

    login: str
    password: str
