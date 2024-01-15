from dataclasses import dataclass, field
from uuid import UUID

from core.errors import WalletsLimitError, DoesNotExistError
from core.wallet import Wallet
from infra.constants import WALLETS_LIMIT
from infra.in_memory.users import UserInMemory


@dataclass
class WalletsInMemory:
    users: UserInMemory
    wallets: dict[str, list[Wallet]] = field(default_factory=dict)

    def create(self, api_key: str) -> Wallet:
        self.users.try_authorization(api_key)

        wallet = Wallet()
        try:
            if len(self.wallets[api_key]) < WALLETS_LIMIT:
                self.wallets[api_key].append(wallet)
            else:
                raise WalletsLimitError(api_key)

        except KeyError:
            self.wallets[api_key] = [wallet]

        return wallet

    def read(self, address: UUID, api_key: str) -> Wallet:
        self.users.try_authorization(api_key)

        try:
            for wallet in self.wallets[api_key]:
                if str(wallet.address) == str(address):
                    return wallet
            raise DoesNotExistError("Wallet", "Address", str(address))
        except KeyError:
            raise DoesNotExistError("Wallet", "Address", str(address))
