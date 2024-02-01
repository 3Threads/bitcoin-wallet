import pytest
from fastapi.testclient import TestClient

from infra.constants import ADMIN_API_KEY, FAKE_RATE
from runner.setup import init_app
from tests.api.fixture_fuctions import (
    create_user_and_get_key,
    create_wallet_and_get_address,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_get_statistics(client: TestClient) -> None:
    api_key1 = create_user_and_get_key(client)
    api_key2 = create_user_and_get_key(client, "test1@gmail.com")
    wallet_address1 = create_wallet_and_get_address(client, api_key1)
    wallet_address2 = create_wallet_and_get_address(client, api_key2)

    client.post(
        "/transactions",
        headers={"api_key": api_key1},
        json={
            "from_address": wallet_address1,
            "to_address": wallet_address2,
            "transaction_amount": 0.5,
        },
    )

    response = client.get("/statistics", headers={"api_key": ADMIN_API_KEY})

    assert response.status_code == 200

    assert response.json() == {
        "statistic": {
            "total_transactions": 1,
            "profit_btc": 0.0075,
            "profit_usd": 0.0075 * FAKE_RATE,
        }
    }


def test_should_not_get_statistics(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    response = client.get("/statistics", headers={"api_key": api_key})

    assert response.status_code == 401
    assert response.json() == {"error": {"message": f"Invalid API key: {api_key}"}}
