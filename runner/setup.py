import os

from fastapi import FastAPI

from infra.constants import DATABASE_NAME, SQL_FILE

from infra.fastapi.units import unit_api
from infra.in_memory.units import UnitsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.units import UnitsDatabase


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(unit_api)

    if os.getenv("POS_REPOSITORY_KIND", "memory") == "sqlite":
        db = Database(DATABASE_NAME, os.path.abspath(SQL_FILE))
        # db.initial()    Uncomment this if you want to create initial db
        app.state.units = UnitsDatabase(db.get_connection(), db.get_cursor())
    else:
        app.state.units = UnitsInMemory()

    return app
