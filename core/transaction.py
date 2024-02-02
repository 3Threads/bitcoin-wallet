import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from core.errors import NotEnoughBitcoinError, TransactionBetweenSameWalletError
from core.wallet import WalletRepository
from infra.constants import MINIMUM_AMOUNT_OF_BITCOIN


@dataclass
class Transaction:
    from_address: UUID
    to_address: UUID
    transaction_amount: float
    transaction_fee: float


class TransactionRepository(ABC):
    def _prepare_transaction(
        self,
        from_api_key: str,
        from_address: UUID,
        to_address: UUID,
        transaction_amount: float,
        wallets: WalletRepository,
    ) -> Transaction:
        if from_address == to_address:
            raise TransactionBetweenSameWalletError()

        from_wallet = wallets.read(from_address, from_api_key)
        to_wallet = wallets.read(to_address, from_api_key, False)

        transaction_amount = math.ceil(transaction_amount * 10**8) / 10**8

        if from_wallet.get_balance() < transaction_amount:
            raise NotEnoughBitcoinError(from_wallet.address)
        from_new_balance = from_wallet.get_balance() - transaction_amount
        to_new_balance = to_wallet.get_balance() + transaction_amount
        fee = 0.0
        if from_wallet.user_id != to_wallet.user_id:
            fee = transaction_amount * 1.5 / 100
        if fee < MINIMUM_AMOUNT_OF_BITCOIN and fee != 0:
            fee = MINIMUM_AMOUNT_OF_BITCOIN
        to_new_balance -= fee

        wallets.update_balance(from_wallet.address, from_new_balance)
        wallets.update_balance(to_wallet.address, to_new_balance)

        transaction = Transaction(from_address, to_address, transaction_amount, fee)

        return transaction

    @abstractmethod
    def make_transaction(
        self,
        from_api_key: str,
        from_address: UUID,
        to_address: UUID,
        transaction_amount: float,
    ) -> Transaction:
        pass

    @abstractmethod
    def read_all(self, api_key: str) -> list[Transaction]:
        pass

    @abstractmethod
    def get_wallet_transactions(self, api_key: str, address: UUID) -> list[Transaction]:
        pass
