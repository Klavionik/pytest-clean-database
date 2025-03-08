from psycopg import Connection as PGConnection
from pymysql import Connection as MySQLConnection


def test_makes_side_effect(test_connection: MySQLConnection | PGConnection):
    with test_connection.cursor() as cur:
        cur.execute("INSERT INTO foo(baz) VALUES (1);")
        cur.execute("INSERT INTO bar(baz) VALUES (1);")

        cur.execute("SELECT * FROM foo;")
        foo_rows = cur.fetchall()
        cur.execute("SELECT * FROM bar;")
        bar_rows = cur.fetchall()

    assert len(foo_rows)
    assert len(bar_rows)


def test_clean_tables_works(test_connection: MySQLConnection | PGConnection):
    with test_connection.cursor() as cur:
        cur.execute("SELECT * FROM foo;")
        foo_rows = cur.fetchall()
        cur.execute("SELECT * FROM bar;")
        bar_rows = cur.fetchall()

    assert not len(foo_rows)
    assert not len(bar_rows)
