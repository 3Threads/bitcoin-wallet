from dataclasses import dataclass
from sqlite3 import Connection
from sqlite3 import Cursor
from uuid import UUID

from core.errors import (
    TransactionBetweenSameWalletError,
    NotEnoughBitcoinError,
    WalletDoesNotExistError,
)
from core.transaction import Transaction
from infra.constants import MINIMUM_AMOUNT_OF_BITCOIN
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


@dataclass
class TransactionsDataBase:
    con: Connection
    cur: Cursor
    wallets: WalletsDatabase
    users: UsersDatabase

    def make_transaction(
        self,
        from_api_key: str,
        from_address: UUID,
        to_address: UUID,
        transaction_amount: float,
    ) -> Transaction:
        if from_address == to_address:
            raise TransactionBetweenSameWalletError()

        from_wallet = self.wallets.read(from_address, from_api_key)
        to_wallet = self.wallets.read(to_address, from_api_key, False)

        transaction_amount = round(transaction_amount, 8)

        if transaction_amount < MINIMUM_AMOUNT_OF_BITCOIN:
            transaction_amount = MINIMUM_AMOUNT_OF_BITCOIN

        if from_wallet.get_balance() < transaction_amount:
            raise NotEnoughBitcoinError(from_address)
        from_new_balance = from_wallet.get_balance() - transaction_amount
        to_new_balance = to_wallet.get_balance() + transaction_amount
        fee = 0
        if from_wallet.user_id != to_wallet.user_id:
            fee = transaction_amount * 1.5 / 100
        if fee < MINIMUM_AMOUNT_OF_BITCOIN and fee != 0:
            fee = MINIMUM_AMOUNT_OF_BITCOIN
        to_new_balance -= fee

        self.wallets.update_balance(from_address, from_new_balance)
        self.wallets.update_balance(to_address, to_new_balance)
        transaction = Transaction(from_address, to_address, transaction_amount, fee)
        self.cur.execute(
            """
                    INSERT INTO TRANSACTIONS (FROM_ADDRESS, TO_ADDRESS, AMOUNT, FEE)
                    VALUES (?, ?, ?, ?);
                """,
            (str(from_address), str(to_address), transaction_amount, fee),
        )
        self.con.commit()
        return transaction

    def read_all(self, api_key: str) -> list[Transaction]:
        user = self.users.try_authorization(api_key)
        wallets = self.wallets.read_all(api_key)
        transactions = []
        for wallet in wallets:
            self.cur.execute(
                "SELECT * FROM TRANSACTIONS WHERE (FROM_ADDRESS = ? OR TO_ADDRESS = ?)",
                [str(wallet.address), str(wallet.address)],
            )
            result = self.cur.fetchall()
            for row in result:
                transaction = Transaction(UUID(row[1]), UUID(row[2]), row[3], row[4])
                transactions.append(transaction)
        return transactions

    def get_wallet_transactions(self, api_key: str, address: UUID) -> list[Transaction]:
        self.users.try_authorization(api_key)
        self.wallets.read(address, api_key, True)
        self.cur.execute(
            "SELECT * FROM TRANSACTIONS WHERE (FROM_ADDRESS = ? OR TO_ADDRESS = ?)",
            [str(address), str(address)],
        )
        result = self.cur.fetchall()

        transactions = []
        for row in result:
            transaction = Transaction(UUID(row[1]), UUID(row[2]), row[3], row[4])
            transactions.append(transaction)
        return transactions
