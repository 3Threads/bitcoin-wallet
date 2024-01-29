from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.user import generate_api_key

from runner.setup import init_app
from tests.api.fixture_fuctions import create_user_and_get_key, create_wallet_and_get_address


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_should_make_transaction(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    wallet_address1 = create_wallet_and_get_address(client, api_key)
    wallet_address2 = create_wallet_and_get_address(client, api_key)

    response = client.post("/transactions", headers={"api_key": api_key},
                           json={"from_address": wallet_address1, "to_address": wallet_address2,
                                 "transaction_amount": 0.5})

    assert response.status_code == 201
    assert response.json() == {
        "transaction": {"from_address": wallet_address1, "to_address": wallet_address2, "transaction_amount": 0.5,
                        "transaction_fee": 0}}


def test_should_not_make_transaction_without_api_key(client: TestClient) -> None:
    unknown_api_key = generate_api_key()

    response = client.post("/transactions", headers={"api_key": unknown_api_key},
                           json={"from_address": str(uuid4()), "to_address": str(uuid4()),
                                 "transaction_amount": 0.5})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"message": f"Invalid API key: {unknown_api_key}"}
    }


def test_make_transaction_unknown_wallet(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    unknown_wallet_address = str(uuid4())

    response = client.post("/transactions", headers={"api_key": api_key},
                           json={"from_address": unknown_wallet_address, "to_address": str(uuid4()),
                                 "transaction_amount": 0.5})

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Wallet with address<{unknown_wallet_address}> does not exist."}
    }


def test_make_transaction_same_wallet(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    unknown_wallet_address = str(uuid4())

    response = client.post("/transactions", headers={"api_key": api_key},
                           json={"from_address": unknown_wallet_address, "to_address": unknown_wallet_address,
                                 "transaction_amount": 0.5})

    assert response.status_code == 405
    assert response.json() == {
        "error": {"message": f"Transaction between one wallet is restricted."}
    }


def test_make_transaction_with_other_wallet(client: TestClient) -> None:
    api_key1 = create_user_and_get_key(client)
    api_key2 = create_user_and_get_key(client, "test2@gmail.com")
    wallet_address1 = create_wallet_and_get_address(client, api_key1)
    wallet_address2 = create_wallet_and_get_address(client, api_key2)

    response = client.post("/transactions", headers={"api_key": api_key1},
                           json={"from_address": wallet_address2, "to_address": wallet_address1,
                                 "transaction_amount": 0.5})

    assert response.status_code == 403
    assert response.json() == {
        "error": {"message": f"User does not have wallet<{wallet_address2}>."}
    }


def test_make_transaction_not_enough_bitcoin(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    wallet_address1 = create_wallet_and_get_address(client, api_key)
    wallet_address2 = create_wallet_and_get_address(client, api_key)

    response = client.post("/transactions", headers={"api_key": api_key},
                           json={"from_address": wallet_address1, "to_address": wallet_address2,
                                 "transaction_amount": 1.5})

    assert response.status_code == 409
    assert response.json() == {
        "error": {"message": f"Not enough bitcoin on the wallet with address<{wallet_address1}>."}
    }


def test_should_persist_transactions(client: TestClient) -> None:
    api_key = create_user_and_get_key(client)
    wallet_address1 = create_wallet_and_get_address(client, api_key)
    wallet_address2 = create_wallet_and_get_address(client, api_key)

    client.post("/transactions", headers={"api_key": api_key},
                json={"from_address": wallet_address1, "to_address": wallet_address2,
                      "transaction_amount": 0.5})

    response = client.get(f"/transactions", headers={"api_key": api_key})

    assert response.status_code == 200
    assert response.json() == {
        "transactions": [{"from_address": wallet_address1, "to_address": wallet_address2, "transaction_amount": 0.5,
                          "transaction_fee": 0.0}]}


def test_should_read_transactions_without_api_key(client: TestClient) -> None:
    unknown_api_key = generate_api_key()

    response = client.get("/transactions", headers={"api_key": unknown_api_key})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"message": f"Invalid API key: {unknown_api_key}"}
    }
