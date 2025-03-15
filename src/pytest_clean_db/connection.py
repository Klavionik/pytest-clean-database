from __future__ import annotations

import abc
import itertools
import urllib.parse
from typing import Any, Literal, TypedDict

Dialect = Literal["psql", "mysql"]


class CleanDBConnectionError(Exception):
    pass


class MySQLArgs(TypedDict):
    host: str
    port: int
    user: str
    password: str
    database: str
    autocommit: bool


class Connection(abc.ABC):
    @property
    @abc.abstractmethod
    def dialect(self) -> Dialect:
        pass

    @abc.abstractmethod
    def execute(self, query: str) -> Any:
        pass

    @abc.abstractmethod
    def fetch(self, query: str) -> list[str]:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass


class PostgreSQLConnection(Connection):
    def __init__(self, dsn: str) -> None:
        try:
            from psycopg import connect
        except ModuleNotFoundError:
            raise CleanDBConnectionError(
                "Cannot create connection: install psycopg to use PostgreSQL."
            )

        self.dsn = dsn
        self._conn = connect(dsn, autocommit=True)

    @property
    def dialect(self) -> Dialect:
        return "psql"

    def execute(self, query: str) -> Any:
        with self._conn.cursor() as cur:
            cur.execute(query)

    def fetch(self, query: str) -> list[str]:
        with self._conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

        return list(itertools.chain.from_iterable(result))

    def close(self) -> None:
        self._conn.close()


class MySQLConnection(Connection):
    def __init__(self, dsn: str) -> None:
        try:
            from pymysql import connect
        except ModuleNotFoundError:
            raise CleanDBConnectionError(
                "Cannot create connection: install pymysql to use MySQL."
            )

        self.dsn = dsn
        self._conn = connect(**mysql_dsn_to_args(dsn))

    @property
    def dialect(self) -> Dialect:
        return "mysql"

    def execute(self, query: str) -> Any:
        with self._conn.cursor() as cur:
            cur.execute(query)

    def fetch(self, query: str) -> list[str]:
        with self._conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

        return list(itertools.chain.from_iterable(result))

    def close(self) -> None:
        self._conn.close()


def mysql_dsn_to_args(dsn: str) -> MySQLArgs:
    url = urllib.parse.urlparse(dsn)

    if (
        url.hostname is None
        or url.port is None
        or url.username is None
        or url.password is None
    ):
        raise CleanDBConnectionError(f"Incorrect MySQL connection string {dsn}.")

    # TODO: Support connection args from query parameters.
    args = MySQLArgs(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path.lstrip("/"),
        autocommit=True,
    )

    return args


def create_connection(dsn: str) -> Connection:
    try:
        scheme, _ = dsn.rsplit("://")
    except ValueError as exc:
        raise ValueError(f"Cannot detect scheme from connection string {dsn}.") from exc

    if scheme == "postgresql":
        return PostgreSQLConnection(dsn)

    if scheme == "mysql":
        return MySQLConnection(dsn)

    raise CleanDBConnectionError(
        f'Unknown scheme {scheme}. Must be one of: "postgresql", "mysql".'
    )
