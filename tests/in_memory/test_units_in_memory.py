from uuid import uuid4

import pytest

from core.errors import AlreadyExistError, DoesNotExistError
from core.unit import Unit
from infra.in_memory.units import UnitsInMemory


def test_create_unit_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)


def test_create_same_unit_twice_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    with pytest.raises(AlreadyExistError):
        units.create(unit)


def test_read_unit_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    result_unit = units.read(unit.id)
    assert result_unit == unit


def test_read_unknown_unit_in_memory() -> None:
    units = UnitsInMemory()

    with pytest.raises(DoesNotExistError):
        units.read(uuid4())


def test_read_all_unit_in_memory() -> None:
    units = UnitsInMemory()
    unit = Unit("kg")
    units.create(unit)

    assert units.read_all() == [unit]
