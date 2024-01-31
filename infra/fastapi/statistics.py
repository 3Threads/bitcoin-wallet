from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import (
    ErrorMessageEnvelope,
    InvalidApiKeyError,
)
from core.statistic import Statistic
from infra.fastapi.dependables import ApiKey, StatisticRepositoryDependable, ConverterDependable

statistics_api = APIRouter(tags=["Statistics"])


class StatisticItem(BaseModel):
    total_transactions: int
    profit_btc: float
    profit_usd: float


class StatisticEnvelope(BaseModel):
    statistic: StatisticItem


@statistics_api.get(
    "/statistics",
    status_code=200,
    response_model=StatisticEnvelope,
    responses={401: {"model": ErrorMessageEnvelope}},
)
def get_statistics(
        api_key: ApiKey, statistics: StatisticRepositoryDependable, converter: ConverterDependable
) -> JSONResponse | dict[str, dict[str, str | float]]:
    try:
        statistics = statistics.get_statistics(api_key)
        profit_btc = statistics.profit
        profit_usd = profit_btc * converter.get_rate()
        return {"statistic":
            {
                "total_transactions": statistics.total_transactions,
                "profit_btc": profit_btc,
                "profit_usd": profit_usd
            }
        }
    except InvalidApiKeyError as e:
        return e.get_error_json_response(401)
