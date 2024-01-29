from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_user(client: TestClient) -> None:
    response = client.post("/users", json={"email": "test@gmail.com"})

    assert response.status_code == 201
    assert response.json() == {"user": {"id": ANY, "api_key": ANY}}
