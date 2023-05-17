from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import CycleDAO
from egame179_backend.db.user import User
from egame179_backend.db.warehouse import Warehouse, WarehouseDAO

router = APIRouter()


@router.get("/list/user")
async def get_user_warehouses(
    user: User = Depends(get_current_user),
    dao: WarehouseDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
) -> list[Warehouse]:
    """Get warehouses for user.

    Args:
        user (User): authenticated user data.
        dao (WarehouseDAO): warehouses table data access object.
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        list[Warehouse]: warehouses status for user.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id, user=user.id)


@router.get("/list", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_warehouses(dao: WarehouseDAO = Depends()) -> list[Warehouse]:
    """Get warehouse history for all users.

    Args:
        dao (WarehouseDAO): warehouses table data access object.

    Returns:
        list[Warehouse]: warehouses history for all users.
    """
    return await dao.select()
