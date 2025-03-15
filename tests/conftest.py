from __future__ import annotations

from collections.abc import Iterator

import pytest
from psycopg import Connection as PGConnection
from psycopg import connect as pgconnect
from pymysql import Connection as MySQLConnection
from pymysql import connect as mysqlconnect

from pytest_clean_db.connection import mysql_dsn_to_args


@pytest.fixture(scope="session")
def mysql_dsn() -> str:
    return "mysql://root:password@0.0.0.0:3306/test"


@pytest.fixture(scope="session")
def pg_dsn() -> str:
    return "postgresql://postgres:password@0.0.0.0:5432/test"


@pytest.fixture()
def test_database() -> Iterator[None]:
    with mysqlconnect(
        host="0.0.0.0",
        port=3306,
        user="root",
        password="password",
        database="mysql",
        autocommit=True,
    ) as mysql_conn:
        with mysql_conn.cursor() as mysql_cur:
            mysql_cur.execute("DROP DATABASE IF EXISTS test;")
            mysql_cur.execute("CREATE DATABASE test;")

    with pgconnect(
        "postgresql://postgres:password@0.0.0.0:5432/postgres",
        autocommit=True,
    ) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            pg_cur.execute("DROP DATABASE IF EXISTS test;")
            pg_cur.execute("CREATE DATABASE test;")

    yield

    with mysqlconnect(
        host="0.0.0.0",
        port=3306,
        user="root",
        password="password",
        database="mysql",
        autocommit=True,
    ) as mysql_conn:
        with mysql_conn.cursor() as mysql_cur:
            mysql_cur.execute("DROP DATABASE test;")

    with pgconnect(
        "postgresql://postgres:password@0.0.0.0:5432/postgres",
        autocommit=True,
    ) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            pg_cur.execute("DROP DATABASE test;")


@pytest.fixture()
def pg_connection(test_database: None, pg_dsn: str) -> Iterator[PGConnection]:
    with pgconnect(
        pg_dsn,
        autocommit=True,
    ) as pg_conn:
        yield pg_conn


@pytest.fixture()
def mysql_connection(test_database: None, mysql_dsn: str) -> Iterator[MySQLConnection]:
    with mysqlconnect(**mysql_dsn_to_args(mysql_dsn)) as mysql_conn:
        yield mysql_conn
