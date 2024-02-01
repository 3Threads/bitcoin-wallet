from dataclasses import dataclass, field
from uuid import UUID

from core.errors import WalletDoesNotExistError, WalletPermissionError, WalletsLimitError
from core.wallet import Wallet
from infra.constants import WALLETS_LIMIT
from infra.in_memory.users import UsersInMemory


@dataclass
class WalletsInMemory:
    users: UsersInMemory
    wallets: dict[UUID, Wallet] = field(default_factory=dict)

    def create(self, api_key: str) -> Wallet:
        user = self.users.try_authorization(api_key)

        wallet = Wallet(user.id)

        users_wallets_num = 0
        for curr_wallet in self.wallets.values():
            if curr_wallet.user_id == user.id:
                users_wallets_num += 1

        if users_wallets_num < WALLETS_LIMIT:
            self.wallets[wallet.address] = wallet
        else:
            raise WalletsLimitError(api_key)

        return wallet

    def read(
            self, address: UUID, api_key: str, check_permission: bool = True
    ) -> Wallet:
        user = self.users.try_authorization(api_key)
        try:
            wallet = self.wallets[address]
            if check_permission and wallet.user_id != user.id:
                raise WalletPermissionError(address)
            return wallet
        except KeyError:
            raise WalletDoesNotExistError(address)

    def update_balance(self, address: UUID, new_balance: float) -> None:
        wallet = self.wallets[address]
        wallet.balance = new_balance
        self.wallets[address] = wallet

    def read_all(self, api_key: str) -> list[Wallet]:
        user = self.users.try_authorization(api_key)
        wallets = []
        for wallet in self.wallets.values():
            if wallet.user_id == user.id:
                wallets.append(wallet)
        return wallets

