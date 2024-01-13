from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_unit(client: TestClient) -> None:
    unit = {"name": "კგ"}

    response = client.post("/units", json=unit)

    assert response.status_code == 201
    assert response.json() == {"unit": {"id": ANY, **unit}}


def test_should_not_create_unit_that_exists(client: TestClient) -> None:
    unit = {"name": "კგ"}

    client.post("/units", json=unit)
    response = client.post("/units", json=unit)

    assert response.status_code == 409
    assert response.json() == {
        "error": {"message": f"Unit with name<{unit['name']}> already exists."}
    }


def test_should_not_read_unknown_unit(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(f"/units/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Unit with id<{unknown_id}> does not exist."}
    }


def test_should_persist_unit(client: TestClient) -> None:
    unit = {"name": "კგ"}

    response = client.post("/units", json=unit)
    unit_id = response.json()["unit"]["id"]

    response = client.get(f"/units/{unit_id}")

    assert response.status_code == 200
    assert response.json() == {"unit": {"id": unit_id, **unit}}


def test_get_all_units_on_empty(client: TestClient) -> None:
    response = client.get("/units")

    assert response.status_code == 200
    assert response.json() == {"units": []}


def test_get_all_units(client: TestClient) -> None:
    unit = {"name": "კგ"}

    response = client.post("/units", json=unit)
    unit_id = response.json()["unit"]["id"]

    response = client.get("/units")

    assert response.status_code == 200
    assert response.json() == {"units": [{"id": unit_id, **unit}]}
