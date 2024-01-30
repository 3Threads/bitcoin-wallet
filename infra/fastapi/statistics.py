from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import (
    DoesNotExistError,
    ErrorMessageEnvelope,
    InvalidApiKeyError,
    NotEnoughBitcoinError,
    TransactionBetweenSameWalletError,
    WalletPermissionError,
)
from core.statistic import Statistic

from core.transaction import Transaction
from infra.fastapi.dependables import ApiKey, TransactionRepositoryDependable, StatisticRepositoryDependable

statistics_api = APIRouter(tags=["Statistics"])


class StatisticItem(BaseModel):
    total_transactions: int
    profit: float


class StatisticEnvelope(BaseModel):
    statistic: StatisticItem


@statistics_api.post(
    "/statistics",
    status_code=201,
    response_model=StatisticEnvelope,
    responses={401: {"model": ErrorMessageEnvelope}}
)
def get_statistics(
        api_key: ApiKey, statistics: StatisticRepositoryDependable
) -> dict[str, Statistic] | JSONResponse:
    try:
        return {"statistic": statistics.get_statistics(api_key)}
    except InvalidApiKeyError as e:
        return e.get_error_json_response(401)
