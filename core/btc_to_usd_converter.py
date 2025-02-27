from dataclasses import dataclass
from typing import Protocol

import httpx

from infra.constants import FAKE_RATE


class CryptoExchangeRate(Protocol):
    def get_rate(self) -> float:
        pass


@dataclass
class APICryptoExchangeRate:
    def get_rate(self) -> float:
        response = httpx.get(
            "https://api.coinconvert.net/convert/btc/usd",
            params={"amount": 1},
        )

        return float(response.json()["USD"])


@dataclass
class FakeCryptoExchangeRate:
    rate: float = FAKE_RATE

    def get_rate(self) -> float:
        return self.rate
