# pytest-clean-db
A pytest fixture that provides a clear and concise way to help you clean up your test 
database after each test, maintaining a proper test isolation.

# Installation
pytest-clean-db requires Python >=3.8 and pytest >=7.0.

There is support for two databases, PostgreSQL and MySQL.

To install with support for PostgreSQL (using Psycopg3):
```shell
pip install pytest-clean-db[psql]
```

To install with support for MySQL (using PyMySQL):
```shell
pip install pytest-clean-db[mysql]
```

Or both:
```shell
pip install pytest-clean-db[psql,mysql]
```

# Usage
Create fixture `clean_db_urls`, exposing database connection strings (in other words, 
DSNs) for every PostgreSQL/MySQL test database you're using during the test run.

Use `postgresql://` scheme for PostgreSQL and `mysql://` scheme for MySQL.

**IMPORTANT!** Make sure that this fixture requires the fixture responsible for creating
your test database and running migrations on it. See `Mode of operation` for explanation.

Example:
```python
# myproject/tests/conftest.py

@pytest.fixture()
def test_db():
    run_create_database()
    run_migrations()
    
    yield 
    
    drop_database()
    
@pytest.fixture(scope="session")
def clean_db_urls(test_db):
    return [
        "postgresql://username:password@localhost:5432/test", 
        "mysql://username:password@localhost:3306/test"
    ]
```

_PostgreSQL note:_ by default, `public` schema will be used. To change the schema, 
you can pass it via `--clean-db-pg-schema` argument to pytest.

# Mode of operation


# Rationale
When you develop an application that makes use of a database, most likely you will end up
having at least a few test cases that somehow operate on your test database, creating 
side effects (like inserting and updating rows). That means, to keep your tests properly 
isolated from each other you have to undo the side effects made during the previous test
and start your next test with a blank slate.

Some frameworks provide users with means to do that: for example, Django takes care of 
keeping your test database fresh and clean, so you don't have to worry about it.
But if you're using, say, FastAPI and SQLAlchemy, or even Blacksheep and asyncpg (a 
database driver), you are on your own to create the solution to this problem.

The solution might be as simple as recreating the test database for every test, but 
as the size of the test suite grows, this will become slower. `TRUNCATE TABLE ...` 
improves the performance a bit, but if you have tens and hunders of tables, truncating 
every one of them on every test still will be unacceptably slow.

Hence, this fixture.
