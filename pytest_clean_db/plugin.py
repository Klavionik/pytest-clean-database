from collections.abc import Iterable, Iterator
from typing import Literal

import pytest

from pytest_clean_db import Connection
from pytest_clean_db.dialect import mysql, postgres

Dialect: Literal["psql", "mysql"]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("clean_db")
    group.addoption(
        "--clean-db-dialect",
        default="pg",
        help="Choose database dialect.",
        choices=("pg", "mysql"),
    )
    group.addoption(
        "--clean-db-pg-schema", default="public", help="Set schema for PostgreSQL."
    )


@pytest.fixture(scope="session", autouse=True)
def setup_tracing(
    request: pytest.FixtureRequest, clean_db_connections: Iterable[Connection]
) -> None:
    match request.config.option.clean_db_dialect:
        case "pg":
            postgres.setup_tracing(
                request.config.option.clean_db_pg_schema, clean_db_connections
            )
        case "mysql":
            mysql.setup_tracing(clean_db_connections)
        case _:
            raise ValueError("Unknown database dialect. Use one of 'pg' or 'mysql'.")


@pytest.fixture(autouse=True)
def run_clean_tables(
    request: pytest.FixtureRequest, clean_db_connections: Iterable[Connection]
) -> Iterator[None]:
    yield

    match request.config.option.clean_db_dialect:
        case "pg":
            postgres.run_clean_tables(
                request.config.option.clean_db_pg_schema, clean_db_connections
            )
        case "mysql":
            mysql.run_clean_tables(clean_db_connections)
        case _:
            raise ValueError("Unknown database dialect. Use one of 'pg' or 'mysql'.")
