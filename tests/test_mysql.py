from pymysql import Connection


def test_check_dirty_table_created(mysql_connection: Connection):
    with mysql_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.tables
            WHERE table_name = '__dirty_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


def test_check_trigger_created(mysql_connection: Connection):
    with mysql_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.triggers
            WHERE trigger_name LIKE 'mark_dirty_%'
            """
        )
        result = cur.fetchall()

    assert len(result) == 2


def test_check_mark_dirty_function_created(mysql_connection: Connection):
    with mysql_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.routines
            WHERE routine_name = 'mark_dirty';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1


def test_check_clean_tables_function_created(mysql_connection: Connection):
    with mysql_connection.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM information_schema.routines
            WHERE routine_name = 'clean_tables';
            """
        )
        result = cur.fetchall()

    assert len(result) == 1
