import pytest
from psycopg import Connection as PsycopgConnection
from pymysql import Connection as PyMySQLConnection

CONFTEST = """
from __future__ import annotations

from collections.abc import Iterator

import pytest
from psycopg import Connection as PGConnection
from psycopg import connect as pgconnect
from pymysql import Connection as MySQLConnection
from pymysql import connect as mysqlconnect


@pytest.fixture(scope="session", params=["psql", "mysql"])
def test_connection(
    request: pytest.FixtureRequest,
) -> Iterator[MySQLConnection | PGConnection]:
    if request.param == "psql":
        with pgconnect(
            "postgresql://postgres:password@0.0.0.0:5432/test",
            autocommit=True,
        ) as pg_conn:
            yield pg_conn
    elif request.param == "mysql":
        with mysqlconnect(
            host="0.0.0.0",
            port=3306,
            user="root",
            password="password",
            database="test",
            autocommit=True,
        ) as mysql_conn:
            yield mysql_conn
    else:
        raise RuntimeError


@pytest.fixture(scope="session")
def clean_db_urls() -> list[str]:
    return [
        "postgresql://postgres:password@0.0.0.0:5432/test",
        "mysql://root:password@0.0.0.0:3306/test",
    ]
"""

TESTS = """
from __future__ import annotations

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
"""


@pytest.mark.usefixtures("test_database")
def test_clean_db_plugin(
    pg_connection: PsycopgConnection,
    mysql_connection: PyMySQLConnection,
    pytester: pytest.Pytester,
) -> None:
    pg_connection.execute("CREATE TABLE foo (baz BIGINT);")
    pg_connection.execute("CREATE TABLE bar (baz BIGINT);")

    with mysql_connection.cursor() as cur:
        cur.execute("CREATE TABLE foo (baz BIGINT);")
        cur.execute("CREATE TABLE bar (baz BIGINT);")

    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(TESTS)

    result = pytester.runpytest()
    result.assert_outcomes(passed=4)
