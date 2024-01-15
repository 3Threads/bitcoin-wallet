from fastapi import APIRouter
from pydantic import BaseModel

from core.user import User
from infra.fastapi.dependables import UserRepositoryDependable

users_api = APIRouter(tags=["Users"])


class UserItem(BaseModel):
    api_key: str


class UserItemEnvelope(BaseModel):
    user: UserItem


@users_api.post(
    "/users",
    status_code=201,
    response_model=UserItemEnvelope
)
def register_user(
        users: UserRepositoryDependable
) -> dict[str, User]:
    return {"user": users.create()}
