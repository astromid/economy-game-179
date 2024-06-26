from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import SyncStatusDAO
from egame179_backend.db.user import User

router = APIRouter()


@router.get("/health")
def health_check() -> None:
    """Check the health of a project.

    It returns 200 if the project is healthy.
    """


@router.get("/sync/status", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_sync_status(dao: SyncStatusDAO = Depends()) -> dict[int, bool]:
    """Get users sync statuses.

    Args:
        dao (SyncStatusDAO): sync status table DAO.

    Returns:
        dict[int, bool]: {user: synced}
    """
    statuses = await dao.select()
    return {status.user: status.synced for status in statuses}


@router.get("/sync")
async def sync(user: User = Depends(get_current_user), dao: SyncStatusDAO = Depends()) -> None:
    """Sync user.

    Args:
        user (User): authenticated user data.
        dao (SyncStatusDAO): sync status table DAO.
    """
    await dao.sync(user.id)
