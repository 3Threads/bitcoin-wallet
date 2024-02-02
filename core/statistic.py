from dataclasses import dataclass
from typing import Protocol


@dataclass
class Statistic:
    total_transactions: int
    profit: float


class StatisticRepository(Protocol):
    def get_statistic(self, admin_api_key: str) -> Statistic:
        pass
