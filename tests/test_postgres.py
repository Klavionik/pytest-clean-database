from psycopg import Connection


def test_check_dirty_table_created(pg_connection: Connection):
    with pg_connection.cursor() as cur:
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


def test_check_trigger_created(pg_connection: Connection):
    with pg_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_trigger
            JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
            WHERE relname IN ('foo', 'bar') AND tgname = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 2


def test_check_mark_dirty_function_created(pg_connection: Connection):
    with pg_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_proc WHERE proname = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


def test_check_clean_tables_function_created(pg_connection: Connection):
    with pg_connection.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM pg_proc WHERE proname = 'clean_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1
