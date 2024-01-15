from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import ErrorMessageEnvelope, AlreadyExistError
from core.unit import Unit
from infra.fastapi.dependables import UnitRepositoryDependable, UserRepositoryDependable

users_api = APIRouter(tags=["Users"])


class UserItem(BaseModel):
    api_key: str


class UserItemEnvelope(BaseModel):
    user: UserItem


@users_api.post(
    "/users",
    status_code=201,
    response_model=UserItemEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def create_unit(
        users: UserRepositoryDependable
) -> dict[str, Unit] | JSONResponse:
    try:
        return {"user": users.create()}
    except AlreadyExistError as e:
        return e.get_error_json_response(409)
