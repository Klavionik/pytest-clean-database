import pytest

from pytest_clean_db.connection import (
    CleanDBConnectionError,
    MySQLConnection,
    PostgreSQLConnection,
    create_connection,
    mysql_dsn_to_args,
)


@pytest.mark.usefixtures("test_database")
def test_create_psql_conn(pg_dsn: str) -> None:
    conn = create_connection(pg_dsn)

    assert isinstance(conn, PostgreSQLConnection)

    conn.close()


@pytest.mark.usefixtures("test_database")
def test_create_mysql_conn(mysql_dsn: str) -> None:
    conn = create_connection(mysql_dsn)

    assert isinstance(conn, MySQLConnection)

    conn.close()


def test_create_conn_unknown_scheme() -> None:
    url = "nonsense://user:password@0.0.0.0:1000/wtf"

    with pytest.raises(
        CleanDBConnectionError,
        match='Unknown scheme nonsense. Must be one of: "postgresql", "mysql".',
    ):
        create_connection(url)


def test_create_conn_incorrect_scheme() -> None:
    url = "incorrect"

    with pytest.raises(
        ValueError, match="Cannot detect scheme from connection string incorrect."
    ):
        create_connection(url)


def test_mysql_dsn_to_args_correct_dsn() -> None:
    mysql_dsn = "mysql://user:password@localhost:3306/mysql"
    args = mysql_dsn_to_args(mysql_dsn)

    assert args["user"] == "user"
    assert args["password"] == "password"
    assert args["port"] == 3306
    assert args["database"] == "mysql"


def test_mysql_dsn_to_args_incorrect_dsn() -> None:
    mysql_dsn = "incorrect"

    with pytest.raises(
        CleanDBConnectionError, match="Incorrect MySQL connection string incorrect."
    ):
        mysql_dsn_to_args(mysql_dsn)
