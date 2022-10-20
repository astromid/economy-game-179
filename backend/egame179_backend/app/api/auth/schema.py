from pydantic import BaseModel


class UserInfo(BaseModel):
    """User model without sensitive information."""

    id: int
    name: str


class Token(BaseModel):
    """Token model."""

    access_token: str
    token_type: str
