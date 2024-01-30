from dataclasses import dataclass

from core.errors import InvalidApiKeyError
from core.statistic import Statistic
from infra.constants import ADMIN_API_KEY
from infra.in_memory.transactions import TransactionsInMemory


@dataclass
class StatisticsInMemory:
    transactions: TransactionsInMemory

    def get_statistics(self, admin_api_key: str) -> Statistic:
        if admin_api_key == ADMIN_API_KEY:
            profit = sum(tr.transaction_fee for tr in self.transactions.transactions)
            statistics = Statistic(len(self.transactions.transactions), profit)
            return statistics
        else:
            raise InvalidApiKeyError(admin_api_key)
