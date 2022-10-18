from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Users table."""

    __tablename__ = "users"  # type: ignore

    id: int = Field(primary_key=True)
    role: str
    name: str
    login: str | None
    password: str | None
