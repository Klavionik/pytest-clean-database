from collections.abc import Iterable, Iterator
from typing import Literal

import pytest

from pytest_clean_db import Connection
from pytest_clean_db.connection import create_connection
from pytest_clean_db.dialect import mysql, postgres

Dialect: Literal["psql", "mysql"]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("clean_db")
    group.addoption(
        "--clean-db-pg-schema", default="public", help="Set schema for PostgreSQL."
    )


@pytest.fixture(scope="session")
def clean_db_connections(clean_db_urls: Iterable[str]) -> Iterator[list[Connection]]:
    connections = [create_connection(url) for url in clean_db_urls]

    yield connections

    for conn in connections:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_tracing(
    request: pytest.FixtureRequest, clean_db_connections: list[Connection]
) -> None:
    for conn in clean_db_connections:
        if conn.dialect == "psql":
            postgres.setup_tracing(request.config.option.clean_db_pg_schema, conn)
        elif conn.dialect == "mysql":
            mysql.setup_tracing(conn)
        else:
            raise ValueError(f"Invalid database dialect {conn.dialect}.")


@pytest.fixture(autouse=True)
def run_clean_tables(
    request: pytest.FixtureRequest, clean_db_connections: list[Connection]
) -> Iterator[None]:
    yield

    for conn in clean_db_connections:
        if conn.dialect == "psql":
            postgres.run_clean_tables(request.config.option.clean_db_pg_schema, conn)
        elif conn.dialect == "mysql":
            mysql.run_clean_tables(conn)
        else:
            raise ValueError(f"Invalid database dialect {conn.dialect}.")
