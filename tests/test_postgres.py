import pytest

from pytest_clean_db.adapters import DBAPIConnection


@pytest.mark.pg
def test_check_dirty_table_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM pg_class
            WHERE relkind = 'r'
            AND relnamespace = 'public'::regnamespace AND relname = '__dirty_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


@pytest.mark.pg
def test_check_trigger_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_trigger
            JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
            WHERE relname IN ('foo', 'bar') AND tgname = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 2


@pytest.mark.pg
def test_check_mark_dirty_function_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_proc WHERE proname = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


@pytest.mark.pg
def test_check_clean_tables_function_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_proc WHERE proname = 'clean_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1
