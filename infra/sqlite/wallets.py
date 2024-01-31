from dataclasses import dataclass
from sqlite3 import Connection, Cursor, IntegrityError
from uuid import UUID

from core.errors import (
    WalletDoesNotExistError,
    InvalidApiKeyError,
    WalletPermissionError,
    WalletsLimitError,
)
from core.wallet import Wallet
from infra.constants import WALLETS_LIMIT
from infra.sqlite.users import UsersDatabase


@dataclass
class WalletsDatabase:
    con: Connection
    cur: Cursor
    users: UsersDatabase

    def create(self, api_key: str) -> Wallet:
        user = self.users.try_authorization(api_key)

        wallet = Wallet(user.id)

        self.cur.execute(
            "SELECT USER_ID FROM WALLETS WHERE USER_ID = ?", [str(user.id)]
        )
        result = self.cur.fetchall()
        if len(result) >= WALLETS_LIMIT:
            raise WalletsLimitError(api_key)
        self.cur.execute(
            "INSERT INTO WALLETS (ADDRESS, USER_ID, BALANCE) VALUES (?, ?, ?)",
            [str(wallet.address), str(wallet.user_id), wallet.balance],
        )

        self.con.commit()
        return wallet

    def read(
        self, address: UUID, api_key: str, check_permission: bool = True
    ) -> Wallet:
        user = self.users.try_authorization(api_key)
        self.cur.execute(
            "SELECT USER_ID, ADDRESS, BALANCE FROM WALLETS WHERE ADDRESS = ?",
            [str(address)],
        )
        result = self.cur.fetchone()
        if result is None:
            raise WalletDoesNotExistError(str(address))

        wallet = Wallet(UUID(result[0]), UUID(result[1]), result[2])
        if check_permission and wallet.user_id != user.id:
            raise WalletPermissionError(address)

        return wallet

    def update_balance(self, address: UUID, new_balance: float) -> None:
        self.cur.execute(
            "UPDATE WALLETS SET BALANCE = ? WHERE ADDRESS = ?",
            [new_balance, str(address)],
        )
        self.con.commit()

    def read_all(self, api_key: str) -> list[Wallet]:
        user = self.users.try_authorization(api_key)
        self.cur.execute("SELECT * FROM WALLETS WHERE USER_ID = ?", [str(user.id)])
        wallets = []
        result = self.cur.fetchall()
        for wallet in result:
            if str(wallet[1]) == str(user.id):
                w = Wallet(UUID(wallet[1]), UUID(wallet[0]), float(wallet[2]))
                wallets.append(w)
        return wallets
