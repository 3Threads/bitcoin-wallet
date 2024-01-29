from fastapi.testclient import TestClient


def create_user_and_get_key(client: TestClient) -> str:
    response = client.post("/users")
    api_key: str = response.json()["user"]["api_key"]
    return api_key


def create_wallet_and_get_address(client: TestClient, api_key: str) -> str:
    response = client.post("/wallets", headers={"api_key": api_key})
    wallet_address = response.json()['wallet']['address']
    return wallet_address
