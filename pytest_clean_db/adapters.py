import dataclasses
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, Self

from pytest_clean_db.connection import Connection


class DBAPICursor(Protocol):
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
    def execute(
        self, operation: str, parameters: Sequence[Any] | Mapping[str, Any] = ..., /
    ) -> object: ...
    def fetchall(self) -> Sequence[Sequence[Any]]: ...


class DBAPIConnection(Protocol):
    def cursor(self) -> DBAPICursor: ...


@dataclasses.dataclass
class DBAPIAdapter(Connection):
    conn: DBAPIConnection

    def execute(self, query: str, *args: Any, **kwagrs: Any) -> Any:
        with self.conn.cursor() as cur:
            cur.execute(query)
