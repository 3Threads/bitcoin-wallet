import uuid
from dataclasses import dataclass, field
from uuid import UUID

from core.errors import WalletsLimitError, ApiKeyDoesNotExistError, AddressDoesNotExistError
from core.wallet import Wallet


@dataclass
class WalletsInMemory:
    wallets: dict[str, list[Wallet]] = field(default_factory=dict)

    def create(self, api_key: str) -> Wallet:
        wallet = Wallet(api_key, uuid.uuid4(), 1)

        try:
            if len(self.wallets[api_key]) < 3:
                self.wallets[api_key].append(wallet)
            else:
                raise WalletsLimitError(api_key)

        except KeyError:
            self.wallets[api_key] = [wallet]
        return wallet

    def read(self, address: UUID, api_key: str) -> Wallet:
        try:
            for wallet in self.wallets[api_key]:
                if str(wallet.address) == str(address):
                    return wallet
            raise AddressDoesNotExistError(address)
        except KeyError:
            raise ApiKeyDoesNotExistError(api_key)
