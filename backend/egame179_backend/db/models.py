from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: int = Field(primary_key=True)
    type: str
    name: str
    login: str | None
    password: str | None
