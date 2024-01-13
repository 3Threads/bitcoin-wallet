import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

from infra.constants import SQL_FILE_TEST


@dataclass
class Database:
    database_name: str
    sql_file: str = SQL_FILE_TEST

    def __post_init__(self) -> None:
        self.con = sqlite3.connect(self.database_name, check_same_thread=False)
        self.con.execute("PRAGMA foreign_keys = 1")
        self.cur = self.con.cursor()

    def initial(self) -> None:
        with open(self.sql_file, "r") as sql_file:
            sql = sql_file.read()
        self.cur.executescript(sql)
        self.con.commit()

    def close_database(self) -> None:
        self.con.close()

    def get_connection(self) -> Connection:
        return self.con

    def get_cursor(self) -> Cursor:
        return self.cur
