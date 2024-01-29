from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from core.user import User
from infra.fastapi.dependables import UserRepositoryDependable

users_api = APIRouter(tags=["Users"])


class UserRequest(BaseModel):
    email: str


class UserItem(BaseModel):
    id: UUID
    api_key: str


class UserItemEnvelope(BaseModel):
    user: UserItem


@users_api.post(
    "/users",
    status_code=201,
    response_model=UserItemEnvelope
)
def register_user(
        request: UserRequest,
        users: UserRepositoryDependable
) -> dict[str, User]:
    email = request.email
    return {"user": users.create(email)}
