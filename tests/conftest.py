from collections.abc import Iterator


from psycopg import connect as pgconnect, Connection as PGConnection
from pymysql import connect as mysqlconnect, Connection as MySQLConnection
import pytest


@pytest.fixture(scope="session")
def test_database() -> Iterator[None]:
    with (
        pgconnect(
            "postgresql://postgres:password@0.0.0.0:5432/postgres",
            autocommit=True,
        ) as pg_conn,
        mysqlconnect(
            host="0.0.0.0",
            port=3306,
            user="root",
            password="password",
            database="mysql",
            autocommit=True,
        ) as mysql_conn,
        mysql_conn.cursor() as mysql_cur,
        pg_conn.cursor() as pg_cur,
    ):
        mysql_cur.execute("DROP DATABASE IF EXISTS test;")
        mysql_cur.execute("CREATE DATABASE test;")

        pg_cur.execute("DROP DATABASE IF EXISTS test;")
        pg_cur.execute("CREATE DATABASE test;")

        yield

        mysql_cur.execute("DROP DATABASE test;")
        pg_cur.execute("DROP DATABASE test;")


@pytest.fixture(scope="session")
def test_tables(mysql_connection: MySQLConnection, pg_connection: PGConnection) -> None:
    with mysql_connection.cursor() as mysql_cur, pg_connection.cursor() as pg_cur:
        mysql_cur.execute("CREATE TABLE foo(baz BIGINT);")
        mysql_cur.execute("CREATE TABLE bar(baz BIGINT);")

        pg_cur.execute("CREATE TABLE foo(baz BIGINT);")
        pg_cur.execute("CREATE TABLE bar(baz BIGINT);")


@pytest.fixture(scope="session")
def pg_connection(test_database: None) -> Iterator[PGConnection]:
    with pgconnect(
        "postgresql://postgres:password@0.0.0.0:5432/test",
        autocommit=True,
    ) as pg_conn:
        yield pg_conn


@pytest.fixture(scope="session")
def mysql_connection(test_database: None) -> Iterator[MySQLConnection]:
    with mysqlconnect(
        host="0.0.0.0",
        port=3306,
        user="root",
        password="password",
        database="test",
        autocommit=True,
    ) as mysql_conn:
        yield mysql_conn


@pytest.fixture(scope="session")
def clean_db_urls(test_tables: None) -> list[str]:
    return [
        "postgresql://postgres:password@0.0.0.0:5432/test",
        "mysql://root:password@0.0.0.0:3306/test",
    ]


@pytest.fixture(scope="session", params=["psql", "mysql"])
def test_connection(
    request: pytest.FixtureRequest,
    test_tables: None,
    mysql_connection: MySQLConnection,
    pg_connection: PGConnection,
) -> Iterator[MySQLConnection | PGConnection]:
    match request.param:
        case "psql":
            yield pg_connection
        case "mysql":
            yield mysql_connection
        case _:
            raise RuntimeError
