from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_user(client: TestClient) -> None:
    email = "test@gmail.com"
    response = client.post("/users", json={"email": email})

    assert response.status_code == 201
    assert response.json() == {"user": {"id": ANY, "api_key": ANY, "email": email}}


def test_should_not_create_same_user(client: TestClient) -> None:
    email = "test@gmail.com"
    client.post("/users", json={"email": email})
    response = client.post("/users", json={"email": email})
    assert response.status_code == 409
    assert response.json() == {
        "error": {"message": f"The email: {email} already exists."}}
