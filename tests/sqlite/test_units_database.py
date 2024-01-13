import os
from uuid import uuid4

import pytest

from core.errors import AlreadyExistError, DoesNotExistError
from core.unit import Unit
from infra.constants import SQL_FILE_TEST
from infra.sqlite.database_connect import Database
from infra.sqlite.units import UnitsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_insert_unit(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)
    db.close_database()


def test_create_same_unit_twice(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    with pytest.raises(AlreadyExistError):
        units.create(unit)
    db.close_database()


def test_read_unit(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)
    assert units.read(unit.id) == unit
    db.close_database()


def test_read_unknown_unit(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(DoesNotExistError):
        units.read(uuid4())

    db.close_database()


def test_read_all_unit_in_memory(db: Database) -> None:
    units = UnitsDatabase(db.get_connection(), db.get_cursor())
    unit = Unit("kg")
    units.create(unit)

    assert units.read_all() == [unit]

    db.close_database()
