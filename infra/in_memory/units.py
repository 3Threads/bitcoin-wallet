from dataclasses import dataclass, field
from uuid import UUID

from core.errors import AlreadyExistError, DoesNotExistError
from core.unit import Unit


@dataclass
class UnitsInMemory:
    units: dict[UUID, Unit] = field(default_factory=dict)

    def create(self, unit: Unit) -> None:
        for curr_unit in self.units.values():
            if curr_unit.name == unit.name:
                raise AlreadyExistError("Unit", "name", unit.name)
        self.units[unit.id] = unit

    def read(self, unit_id: UUID) -> Unit:
        try:
            return self.units[unit_id]
        except KeyError:
            raise DoesNotExistError("Unit", "id", str(unit_id))

    def read_all(self) -> list[Unit]:
        return list(self.units.values())
