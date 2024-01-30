import os

from fastapi import FastAPI

from infra.constants import DATABASE_NAME, SQL_FILE
from infra.fastapi.statistics import statistics_api
from infra.fastapi.transactions import transactions_api
from infra.fastapi.users import users_api
from infra.fastapi.wallets import wallets_api
from infra.in_memory.statistics import StatisticsInMemory
from infra.in_memory.transactions import TransactionsInMemory
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.statistics import StatisticsDataBase
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(users_api)
    app.include_router(wallets_api)
    app.include_router(transactions_api)
    app.include_router(statistics_api)

    if os.getenv("WALLET_REPOSITORY_KIND", "memory") == "sqlite":
        db = Database(DATABASE_NAME, os.path.abspath(SQL_FILE))
        # db.initial()    Uncomment this if you want to create initial db
        app.state.users = UsersDatabase(db.get_connection(), db.get_cursor())
        app.state.wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), app.state.users)
        app.state.statistics = StatisticsDataBase(db.get_connection(), db.get_cursor(), app.state.transactions)
    else:
        app.state.users = UsersInMemory()
        app.state.wallets = WalletsInMemory(app.state.users)
        app.state.transactions = TransactionsInMemory(app.state.users, app.state.wallets)
        app.state.statistics = StatisticsInMemory(app.state.transactions)

    return app
