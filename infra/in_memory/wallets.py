from dataclasses import dataclass, field
from uuid import UUID

from core.errors import WalletsLimitError, DoesNotExistError, WalletPermissionError
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

    def read(self, address: UUID, api_key: str, check_permission: bool = True) -> Wallet:
        user = self.users.try_authorization(api_key)
        try:
            wallet = self.wallets[address]
            if check_permission and wallet.user_id != user.id:
                raise WalletPermissionError(address)
            return wallet
        except KeyError:
            raise DoesNotExistError("Wallet", "Address", str(address))
