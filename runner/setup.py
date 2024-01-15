import os

from fastapi import FastAPI

from infra.constants import DATABASE_NAME, SQL_FILE
from infra.fastapi.transactions import transactions_api

from infra.fastapi.units import unit_api
from infra.fastapi.users import users_api
from infra.fastapi.wallets import wallets_api
from infra.in_memory.transactions import TransactionInMemory
from infra.in_memory.units import UnitsInMemory
from infra.in_memory.users import UserInMemory
from infra.in_memory.wallets import WalletsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.units import UnitsDatabase


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(unit_api)
    app.include_router(users_api)
    app.include_router(wallets_api)
    app.include_router(transactions_api)

    if os.getenv("WALLET_REPOSITORY_KIND", "memory") == "sqlite":
        db = Database(DATABASE_NAME, os.path.abspath(SQL_FILE))
        # db.initial()    Uncomment this if you want to create initial db
        app.state.units = UnitsDatabase(db.get_connection(), db.get_cursor())
    else:
        app.state.units = UnitsInMemory()
        app.state.users = UserInMemory()
        app.state.wallets = WalletsInMemory()
        app.state.transactions = TransactionInMemory()

    return app
