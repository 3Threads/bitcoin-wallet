from fastapi.testclient import TestClient


def create_user_and_get_key(client: TestClient, email: str = "test@gmail.com") -> str:
    response = client.post("/users", json={"email": email})

    api_key: str = response.json()["user"]["api_key"]
    return api_key
