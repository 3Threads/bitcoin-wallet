from dataclasses import dataclass
from sqlite3 import Connection, Cursor, IntegrityError
from uuid import UUID

from core.errors import AlreadyExistError, DoesNotExistError
from core.unit import Unit


@dataclass
class UnitsDatabase:
    con: Connection
    cur: Cursor

    def create(self, unit: Unit) -> None:
        try:
            self.cur.executemany(
                "insert into units(id, name) values (?,?)",
                [(str(unit.id), unit.name)],
            )
        except IntegrityError:
            raise AlreadyExistError("Unit", "name", unit.name)
        self.con.commit()

    def read(self, unit_id: UUID) -> Unit:
        res = self.cur.execute("select * from units where id = ?", [str(unit_id)])
        result = res.fetchone()
        if result is not None and result[0] is not None:
            return Unit(result[1], UUID(result[0]))
        else:
            raise DoesNotExistError("Unit", "id", str(unit_id))

    def read_all(self) -> list[Unit]:
        units = []
        res = self.cur.execute("select * from units")
        for row in res.fetchall():
            (
                id,
                name,
            ) = row
            units.append(Unit(name, UUID(id)))
        return units
