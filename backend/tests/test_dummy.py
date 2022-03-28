import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from egame179_backend.db.dao.dummy_dao import DummyDAO


@pytest.mark.asyncio
async def test_creation(
    fastapi_app: FastAPI,
    client: TestClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance creation."""
    url = fastapi_app.url_path_for("create_dummy_model")
    test_name = uuid.uuid4().hex
    response = client.put(
        url,
        json={
            "name": test_name,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = DummyDAO(dbsession)
    instances = await dao.filter(name=test_name)
    assert instances[0].name == test_name


@pytest.mark.asyncio
async def test_getting(
    fastapi_app: FastAPI,
    client: TestClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance retrieval."""
    dao = DummyDAO(dbsession)
    test_name = uuid.uuid4().hex
    await dao.create_dummy_model(name=test_name)

    url = fastapi_app.url_path_for("get_dummy_models")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["name"] == test_name
