from collections.abc import Iterable

from tests.conftest import FakeConnectionState, FakeConnection


def test_machinery_initialized(clean_db_connections: Iterable[FakeConnection]) -> None:
    expected_state = (
        FakeConnectionState.TABLE_CREATED
        | FakeConnectionState.MARK_DIRTY_FUNCTION_CREATED
        | FakeConnectionState.TRIGGER_CREATED
        | FakeConnectionState.CLEAN_TABLES_FUNCTION_CREATED
    )

    for conn in clean_db_connections:
        assert conn.state == expected_state


def test_cleanup_fixture_runs(clean_db_connections: Iterable[FakeConnection]) -> None:
    for conn in clean_db_connections:
        assert conn.clean_tables_calls == 1
