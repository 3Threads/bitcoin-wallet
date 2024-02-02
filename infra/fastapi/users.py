from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import EmailAlreadyExistError, ErrorMessageEnvelope
from core.user import User
from infra.fastapi.dependables import UserRepositoryDependable

users_api = APIRouter(tags=["Users"])


class UserRequest(BaseModel):
    email: str


class UserItem(BaseModel):
    id: UUID
    email: str
    api_key: str


class UserItemEnvelope(BaseModel):
    user: UserItem


@users_api.post(
    "/users",
    status_code=201,
    response_model=UserItemEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def register_user(
    request: UserRequest, users: UserRepositoryDependable
) -> dict[str, User] | JSONResponse:
    email = request.email
    try:
        return {"user": users.create(email)}
    except EmailAlreadyExistError as e:
        return e.get_error_json_response()
