import enum
from collections.abc import Iterable
import dataclasses

from pytest_clean_db import queries
import pytest


class FakeConnectionState(enum.IntFlag):
    TABLE_CREATED = enum.auto()
    MARK_DIRTY_FUNCTION_CREATED = enum.auto()
    TRIGGER_CREATED = enum.auto()
    CLEAN_TABLES_FUNCTION_CREATED = enum.auto()


@dataclasses.dataclass
class FakeConnection:
    state: FakeConnectionState = FakeConnectionState(0)
    clean_tables_calls: int = 0

    def fetch(self, query: str) -> Iterable[dict[str, str]]:
        return [{"name": "test_table"}]

    def execute(self, query: str) -> None:
        if query == queries.CREATE_DIRTY_TABLE:
            self.state = self.state | FakeConnectionState.TABLE_CREATED
        elif query == queries.CREATE_MARK_DIRTY_FUNCTION:
            self.state = self.state | FakeConnectionState.MARK_DIRTY_FUNCTION_CREATED
        elif query == queries.CREATE_MARK_DIRTY_TRIGGER % "test_table":
            self.state = self.state | FakeConnectionState.TRIGGER_CREATED
        elif query == queries.CREATE_CLEAN_TABLES_FUNCTION:
            self.state = self.state | FakeConnectionState.CLEAN_TABLES_FUNCTION_CREATED
        elif query == queries.EXECUTE_CLEAN_TABLES:
            self.clean_tables_calls += 1
        else:
            raise ValueError("Unknown query.")

        return None


@pytest.fixture(scope="session")
def clean_db_connections() -> Iterable[FakeConnection]:
    return [FakeConnection(), FakeConnection()]
