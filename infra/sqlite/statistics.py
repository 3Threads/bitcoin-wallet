from dataclasses import dataclass
from sqlite3 import Connection, Cursor

from core.errors import InvalidApiKeyError
from core.statistic import Statistic
from infra.constants import ADMIN_API_KEY
from infra.sqlite.transactions import TransactionsDataBase


@dataclass
class StatisticsDataBase:
    con: Connection
    cur: Cursor
    transactions: TransactionsDataBase

    def get_statistics(self, admin_api_key: str) -> Statistic:
        if admin_api_key == ADMIN_API_KEY:
            profit = self.cur.execute("SELECT SUM(FEE) FROM TRANSACTIONS").fetchone()
            total_transactions = self.cur.execute("SELECT COUNT() FROM TRANSACTIONS").fetchone()
            statistics = Statistic(total_transactions, profit)
            return statistics
        else:
            raise InvalidApiKeyError(admin_api_key)
