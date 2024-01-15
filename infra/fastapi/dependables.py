from typing import Annotated

from fastapi import Depends, Header
from fastapi.requests import Request

from core.unit import UnitRepository


def get_unit_repository(request: Request) -> UnitRepository:
    return request.app.state.units  # type: ignore


UnitRepositoryDependable = Annotated[UnitRepository, Depends(get_unit_repository)]

ApiKey = Annotated[str, Header(convert_underscores=False)]
