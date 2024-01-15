from typing import Annotated

from fastapi import Depends, Header
from fastapi.requests import Request

from core.transaction import TransactionRepository
from core.unit import UnitRepository
from core.wallet import WalletRepository


def get_unit_repository(request: Request) -> UnitRepository:
    return request.app.state.units  # type: ignore


UnitRepositoryDependable = Annotated[UnitRepository, Depends(get_unit_repository)]


def get_transaction_repository(request: Request) -> TransactionRepository:
    return request.app.state.transactions  # type: ignore


TransactionRepositoryDependable = Annotated[TransactionRepository, Depends(get_transaction_repository)]


def get_wallet_repository(request: Request) -> WalletRepository:
    return request.app.state.wallets  # type: ignore


WalletRepositoryDependable = Annotated[WalletRepository, Depends(get_wallet_repository())]

ApiKey = Annotated[str, Header(convert_underscores=False)]
