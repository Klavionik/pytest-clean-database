from collections.abc import Iterable
import pytest

from pytest_clean_db import queries
from typing import Any, Protocol, Iterator


class Connection(Protocol):
    def execute(self, query: str) -> Any:
        pass

    def fetch(self, query: str) -> Iterable[dict[str, str]]:
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_tracing(clean_db_connections: Iterable[Connection]) -> None:
    for conn in clean_db_connections:
        conn.execute(queries.CREATE_DIRTY_TABLE)
        conn.execute(queries.CREATE_MARK_DIRTY_FUNCTION)
        conn.execute(queries.CREATE_CLEAN_TABLES_FUNCTION)

        for table in conn.fetch(queries.SELECT_DIRTY_TABLES_NAMES):
            conn.execute(queries.CREATE_MARK_DIRTY_TRIGGER % table["name"])


@pytest.fixture(autouse=True)
def run_clean_tables(clean_db_connections: Iterable[Connection]) -> Iterator[None]:
    yield

    for conn in clean_db_connections:
        conn.execute(queries.EXECUTE_CLEAN_TABLES)
