from fastapi.testclient import TestClient


def create_user_and_get_key(client: TestClient) -> str:
    response = client.post("/users")
    api_key: str = response.json()["user"]["api_key"]
    return api_key
