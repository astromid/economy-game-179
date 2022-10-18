from pydantic import BaseModel


class UserOut(BaseModel):
    """User model without sensitive information."""

    id: int
    role: str
    name: str
