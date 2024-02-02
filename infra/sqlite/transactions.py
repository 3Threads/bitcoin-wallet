from dataclasses import dataclass
from sqlite3 import Connection, Cursor
from uuid import UUID

from core.transaction import Transaction, TransactionRepository
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


@dataclass
class TransactionsDataBase(TransactionRepository):
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
        transaction = self._prepare_transaction(
            from_api_key, from_address, to_address, transaction_amount, self.wallets
        )
        self.cur.execute(
            """
                    INSERT INTO TRANSACTIONS (FROM_ADDRESS, TO_ADDRESS, AMOUNT, FEE)
                    VALUES (?, ?, ?, ?);
                """,
            (
                str(from_address),
                str(to_address),
                transaction.transaction_amount,
                transaction.transaction_fee,
            ),
        )
        self.con.commit()
        return transaction

    def read_all(self, api_key: str) -> list[Transaction]:
        self.users.try_authorization(api_key)
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
