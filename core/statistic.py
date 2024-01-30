from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID


@dataclass
class Statistic:
    total_transactions: int
    profit: float


class StatisticRepository(Protocol):
    def get_statistic(self, admin_api_key: str) -> Statistic:
        pass
