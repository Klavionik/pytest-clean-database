from collections.abc import Iterator


from pytest_clean_db import Connection
from psycopg import connect as pgconnect
from pymysql import connect as mysqlconnect
from pytest_clean_db.adapters import DBAPIAdapter, DBAPIConnection
import pytest


@pytest.fixture(scope="session")
def test_database(default_connection: DBAPIConnection) -> Iterator[None]:
    with default_connection.cursor() as cur:
        cur.execute("DROP DATABASE IF EXISTS test;")
        cur.execute("CREATE DATABASE test;")

    yield

    with default_connection.cursor() as cur:
        pass
        # cur.execute("DROP DATABASE test;")


@pytest.fixture(scope="session")
def test_tables(test_connection: DBAPIConnection) -> None:
    with test_connection.cursor() as cur:
        cur.execute("CREATE TABLE foo(baz BIGINT);")
        cur.execute("CREATE TABLE bar(baz BIGINT);")


@pytest.fixture(scope="session")
def default_connection(request: pytest.FixtureRequest) -> Iterator[DBAPIConnection]:
    match request.config.option.clean_db_dialect:
        case "pg":
            pg = pgconnect(
                "postgresql://postgres:password@0.0.0.0:5432/postgres",
                autocommit=True,
            )
            yield pg
            pg.close()
        case "mysql":
            mysql = mysqlconnect(
                host="0.0.0.0",
                port=3306,
                user="root",
                password="password",
                database="mysql",
                autocommit=True,
            )
            yield mysql
            mysql.close()
        case _:
            raise ValueError("Unknown database dialect. Use one of 'pg' or 'mysql'.")


@pytest.fixture(scope="session")
def test_connection(
    request: pytest.FixtureRequest, test_database: None
) -> Iterator[DBAPIConnection]:
    match request.config.option.clean_db_dialect:
        case "pg":
            pg = pgconnect(
                "postgresql://postgres:password@0.0.0.0:5432/test",
                autocommit=True,
            )
            yield pg
            pg.close()
        case "mysql":
            mysql = mysqlconnect(
                host="0.0.0.0",
                port=3306,
                user="root",
                password="password",
                database="test",
                autocommit=True,
            )
            yield mysql
            mysql.close()
        case _:
            raise ValueError("Unknown database dialect. Use one of 'pg' or 'mysql'.")


@pytest.fixture(scope="session")
def clean_db_connections(
    test_connection: DBAPIConnection, test_tables: None
) -> list[Connection]:
    return [DBAPIAdapter(test_connection)]
