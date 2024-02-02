from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.user import generate_api_key
from infra.constants import FAKE_RATE, STARTING_BITCOIN_AMOUNT, WALLETS_LIMIT
from runner.setup import init_app
from tests.api.fixture_fuctions import (
    create_user_and_get_key,
    create_wallet_and_get_address,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_create_wallet(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)

    response = client.post("/wallets", headers={"api_key": api_key})

    assert response.status_code == 201
    assert response.json() == {
        "wallet": {
            "address": ANY,
            "balance_btc": STARTING_BITCOIN_AMOUNT,
            "balance_usd": STARTING_BITCOIN_AMOUNT * FAKE_RATE,
        }
    }


def test_should_not_create_product_above_limit(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)

    for i in range(WALLETS_LIMIT):
        response = client.post("/wallets", headers={"api_key": api_key})
        assert response.status_code == 201

    response = client.post("/wallets", headers={"api_key": api_key})
    assert response.status_code == 409
    assert response.json() == {
        "error": {"message": f"User<{api_key}> reached wallets limit({WALLETS_LIMIT})."}
    }


def test_should_not_create_without_api_key(client: TestClient) -> None:
    unknown_api_key = generate_api_key()
    response = client.post("/wallets", headers={"api_key": unknown_api_key})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"message": f"Invalid API key: {unknown_api_key}"}
    }


def test_should_not_read_unknown_wallet(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    unknown_id = uuid4()
    response = client.get(f"/wallets/{unknown_id}", headers={"api_key": api_key})

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Wallet with address<{unknown_id}> does not exist."}
    }


def test_should_persist_wallet(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)

    response = client.post("/wallets", headers={"api_key": api_key})
    wallet_address = response.json()["wallet"]["address"]
    response = client.get(f"/wallets/{wallet_address}", headers={"api_key": api_key})

    assert response.status_code == 200
    assert response.json() == {
        "wallet": {
            "address": wallet_address,
            "balance_btc": STARTING_BITCOIN_AMOUNT,
            "balance_usd": STARTING_BITCOIN_AMOUNT * FAKE_RATE,
        }
    }


def test_should_not_read_with_invalid_key_wallet(client: TestClient) -> None:
    unknown_api_key = generate_api_key()
    response = client.get(f"/wallets/{uuid4()}", headers={"api_key": unknown_api_key})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"message": f"Invalid API key: {unknown_api_key}"}
    }


def test_should_not_read_others_wallet(client: TestClient) -> None:
    api_key1 = create_user_and_get_key(client)
    api_key2 = create_user_and_get_key(client, "test1@gmail.com")

    response = client.post("/wallets", headers={"api_key": api_key1})
    wallet_address = response.json()["wallet"]["address"]
    response = client.get(f"/wallets/{wallet_address}", headers={"api_key": api_key2})

    assert response.status_code == 403
    assert response.json() == {
        "error": {"message": f"User does not have wallet<{wallet_address}>."}
    }


def test_should_get_wallet_transactions(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    wallet_address1 = create_wallet_and_get_address(client, api_key)
    wallet_address2 = create_wallet_and_get_address(client, api_key)

    response = client.post(
        "/transactions",
        headers={"api_key": api_key},
        json={
            "from_address": wallet_address1,
            "to_address": wallet_address2,
            "transaction_amount": 0.5,
        },
    )

    response = client.get(
        f"/wallets/{wallet_address1}/transactions", headers={"api_key": api_key}
    )

    assert response.status_code == 200
    assert response.json() == {
        "transactions": [
            {
                "from_address": wallet_address1,
                "to_address": wallet_address2,
                "transaction_amount": 0.5,
                "transaction_fee": 0.0,
            }
        ]
    }


def test_should_not_get_wallet_transactions_with_invalid_key(
    client: TestClient,
) -> None:
    unknown_api_key = generate_api_key()
    response = client.get(
        f"/wallets/{uuid4()}/transactions", headers={"api_key": unknown_api_key}
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {"message": f"Invalid API key: {unknown_api_key}"}
    }


def test_should_not_get_others_wallet_transactions(client: TestClient) -> None:
    api_key1 = create_user_and_get_key(client)
    api_key2 = create_user_and_get_key(client, "test1@gmail.com")
    wallet_address2 = create_wallet_and_get_address(client, api_key2)
    response = client.get(
        f"/wallets/{wallet_address2}/transactions", headers={"api_key": api_key1}
    )

    assert response.status_code == 403
    assert response.json() == {
        "error": {"message": f"User does not have wallet<{wallet_address2}>."}
    }


def test_should_not_get_invalid_wallet_transactions(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    wallet_address = str(uuid4())
    response = client.get(
        f"/wallets/{wallet_address}/transactions", headers={"api_key": api_key}
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Wallet with address<{wallet_address}> does not exist."}
    }
