import pytest

from pytest_clean_db.adapters import DBAPIConnection


@pytest.mark.mysql
def test_check_dirty_table_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.tables
            WHERE table_name = '__dirty_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


@pytest.mark.mysql
def test_check_trigger_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.triggers
            """
        )
        result = cur.fetchall()
        print(result)

    assert len(result) == 2


@pytest.mark.mysql
def test_check_mark_dirty_function_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.routines
            WHERE routine_name = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


@pytest.mark.mysql
def test_check_clean_tables_function_created(test_connection: DBAPIConnection):
    with test_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.routines
            WHERE routine_name = 'clean_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1
