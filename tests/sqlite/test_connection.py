import os

from infra.constants import SQL_FILE_TEST
from infra.sqlite.database_connect import Database


def test_database_initial_and_close_successful() -> None:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    db.close_database()
