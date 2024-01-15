from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import AlreadyExistError, ErrorMessageEnvelope
from core.unit import Unit
from infra.fastapi.dependables import UnitRepositoryDependable

unit_api = APIRouter(tags=["Units"])


class UnitItem(BaseModel):
    id: UUID
    name: str


class CreateUnitItem(BaseModel):
    name: str


class UnitItemEnvelope(BaseModel):
    unit: UnitItem


class UnitListEnvelope(BaseModel):
    units: list[UnitItem]


@unit_api.post(
    "/units",
    status_code=201,
    response_model=UnitItemEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def create_unit(
    request: CreateUnitItem, units: UnitRepositoryDependable
) -> dict[str, Unit] | JSONResponse:
    unit = Unit(**request.model_dump())
    try:
        units.create(unit)
        return {"unit": unit}
    except AlreadyExistError as e:
        return e.get_error_json_response(409)


@unit_api.get(
    "/units/{unit_id}",
    status_code=200,
    response_model=UnitItemEnvelope,
    responses={404: {"model": ErrorMessageEnvelope}},
)
def read_unit(
    unit_id: UUID, units: UnitRepositoryDependable
) -> dict[str, Unit] | JSONResponse:
    try:
        return {"unit": units.read(unit_id)}
    except DoesNotExistError as e:
        return e.get_error_json_response(404)


@unit_api.get(
    "/units",
    status_code=200,
    response_model=UnitListEnvelope,
)
def read_all_unit(units: UnitRepositoryDependable) -> dict[str, list[Unit]]:
    return {"units": units.read_all()}
