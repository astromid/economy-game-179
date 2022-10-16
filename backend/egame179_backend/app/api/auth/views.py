from fastapi import APIRouter, Depends

from egame179_backend.app.api.auth.schema import AuthData
from egame179_backend.db.dao.users_dao import UserDAO
from egame179_backend.db.models import User

router = APIRouter()


@router.get("/get_users")
async def get_users(user_dao: UserDAO = Depends()) -> list[User]:
    return await user_dao.get_all_users()


@router.post("/auth")
async def auth(auth_data: AuthData, user_dao: UserDAO = Depends()) -> User | None:
    return await user_dao.auth_user(auth_data.login, auth_data.password)
