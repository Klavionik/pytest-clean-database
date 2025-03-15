from psycopg import Connection as PsycopgConnection
from pymysql import Connection as PyMySQLConnection

from pytest_clean_db.connection import MySQLConnection, PostgreSQLConnection
from pytest_clean_db.dialect import mysql
from pytest_clean_db.dialect import postgres as psql


def test_postgresql(pg_connection: PsycopgConnection, pg_dsn: str) -> None:
    pg_connection.execute("CREATE TABLE foo (baz BIGINT);")
    pg_connection.execute("CREATE TABLE bar (baz BIGINT);")
    conn = PostgreSQLConnection(pg_dsn)
    psql.setup_tracing(db_schema="public", conn=conn)
    pg_connection.execute("INSERT INTO foo (baz) VALUES (1);")
    pg_connection.execute("INSERT INTO bar (baz) VALUES (1);")

    psql.run_clean_tables(db_schema="public", conn=conn)

    with pg_connection.cursor() as cur:
        cur.execute("SELECT * FROM foo;")
        foo_rows = cur.fetchall()
        cur.execute("SELECT * FROM bar;")
        bar_rows = cur.fetchall()

    assert len(foo_rows) == 0
    assert len(bar_rows) == 0


def test_mysql(mysql_connection: PyMySQLConnection, mysql_dsn: str) -> None:
    with mysql_connection.cursor() as cur:
        cur.execute("CREATE TABLE foo (baz BIGINT);")
        cur.execute("CREATE TABLE bar (baz BIGINT);")
        conn = MySQLConnection(mysql_dsn)
        mysql.setup_tracing(conn)
        cur.execute("INSERT INTO foo (baz) VALUES (1);")
        cur.execute("INSERT INTO bar (baz) VALUES (1);")

    mysql.run_clean_tables(conn)

    with mysql_connection.cursor() as cur:
        cur.execute("SELECT * FROM foo;")
        foo_rows = cur.fetchall()
        cur.execute("SELECT * FROM bar;")
        bar_rows = cur.fetchall()

    assert len(foo_rows) == 0
    assert len(bar_rows) == 0
