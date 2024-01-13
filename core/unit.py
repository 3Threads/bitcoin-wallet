from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class Unit:
    name: str
    id: UUID = field(default_factory=uuid4)


class UnitRepository(Protocol):
    def create(self, unit: Unit) -> None:
        pass

    def read(self, unit_id: UUID) -> Unit:
        pass

    def read_all(self) -> list[Unit]:
        pass
