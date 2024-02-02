from typing import Annotated

from fastapi import Depends, Header
from fastapi.requests import Request

from core.btc_to_usd_converter import CryptoExchangeRate
from core.statistic import StatisticRepository
from core.transaction import TransactionRepository
from core.user import UserRepository
from core.wallet import WalletRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users  # type: ignore


UserRepositoryDependable = Annotated[UserRepository, Depends(get_user_repository)]

ApiKey = Annotated[str, Header(convert_underscores=False)]


def get_wallet_repository(request: Request) -> WalletRepository:
    return request.app.state.wallets  # type: ignore


WalletRepositoryDependable = Annotated[WalletRepository, Depends(get_wallet_repository)]


def get_transaction_repository(request: Request) -> TransactionRepository:
    return request.app.state.transactions  # type: ignore


TransactionRepositoryDependable = (Annotated)[
    TransactionRepository, Depends(get_transaction_repository)
]


def get_statistic_repository(request: Request) -> StatisticRepository:
    return request.app.state.statistics  # type: ignore


StatisticRepositoryDependable = (Annotated)[
    StatisticRepository, Depends(get_statistic_repository)
]


def get_converter(request: Request) -> CryptoExchangeRate:
    return request.app.state.converter  # type: ignore


ConverterDependable = (Annotated)[CryptoExchangeRate, Depends(get_converter)]
