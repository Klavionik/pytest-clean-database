# pytest-clean-database
A pytest plugin that provides a clear and concise way to help you keep your test 
database clean between tests, maintaining a proper test isolation.

# Installation
pytest-clean-database requires Python >=3.8 and pytest >=7.0.

There is support for two databases, PostgreSQL and MySQL.

To install with support for PostgreSQL (using Psycopg3):
```shell
pip install pytest-clean-database[psql]
```

To install with support for MySQL (using PyMySQL):
```shell
pip install pytest-clean-database[mysql]
```

Or both:
```shell
pip install pytest-clean-database[psql,mysql]
```

# Usage
In your `conftest.py` сreate a new fixture called `clean_db_urls` and make it return a 
sequence of database connection strings (in other words, DSNs) for every PostgreSQL/MySQL 
test database you're using during the test run.

Use `postgresql://` scheme for PostgreSQL and `mysql://` scheme for MySQL.

**IMPORTANT!** Make sure that `clean_db_urls` requires the fixture responsible for 
creating your test database and running migrations on it. See `Mode of operation` for an
explanation.

Example:
```python
# conftest.py

@pytest.fixture()
def test_db():
    create_database()
    run_migrations()
    
    yield 
    
    drop_database()
    
@pytest.fixture(scope="session")
def clean_db_urls(test_db):  # Require test_db fixture.
    return [
        "postgresql://username:password@localhost:5432/test", 
        "mysql://username:password@localhost:3306/test"
    ]
```

_PostgreSQL note:_ by default, `public` schema will be used. To change the schema, 
you can pass it via `--clean-db-pg-schema` argument to pytest.

# Mode of operation
Simply put, the approach for this package is to keep track of changes made to tables 
using database triggers and an internal table, and truncate only the dirty ones. This 
way we do not waste time truncating every table.

There are two steps to the machinery, implemented as [session-scoped](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes) 
[autouse](https://docs.pytest.org/en/stable/how-to/fixtures.html#autouse-fixtures-fixtures-you-don-t-have-to-request) 
fixtures.
1. Set up all database objects that we need - executed only once at the start of the 
   test session.
   1. Create an internal table that keeps track of user tables and their dirtyness.
   2. Create a function that sets the dirty state for a given table.
   3. Create a function that iterates over dirty tables and truncates them, then resets
      the dirty state.
   4. For every user table, create an INSERT trigger that will execute the function that
      marks this table as dirty. 
2. Clean database tables - executed after every test.

For this to work properly it's important to execute the setup step only after the user
tables have been created - otherwise, we won't be able to track their dirtyness. This 
also implies that if you create a table inside a test - it won't be tracked either.
Luckily, pytest fixtures have this incredible feature, where one fixture can 
[request another one](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixtures-can-request-other-fixtures), 
forming a dependency graph. 

When you expose your DSNs via `clean_db_urls` fixture, pytest-clean-database's 
setup fixture requests this fixture. This way you get to decide when the setup happens.
And this is why you must ensure that your `clean_db_urls` fixture requests the fixture 
that sets up your test database. If you set up your test database in some way other than 
pytest fixtures, it still should be possible to create a fixture that blocks until your 
test database is ready.

# Rationale
When you develop an application that makes use of a database, most likely you will end up
having at least a few test cases that somehow operate on your test database, creating 
side effects (like inserting and updating rows). That means, to keep your tests properly 
isolated from each other you have to undo the side effects made during the previous test,
and start your next test with a blank slate.

Some frameworks provide users with means to do that: for example, Django takes care of 
keeping your test database fresh and clean, so you don't have to worry about it.
But if you're using, say, FastAPI and SQLAlchemy, or even Blacksheep and asyncpg (a 
database driver), you are on your own to create the solution to this problem.

The solution might be as simple as recreating the test database for every test, but 
as the size of the test suite grows, this will become slower. `TRUNCATE TABLE ...` 
improves the performance a bit, but if you have tens and hundreds of tables, truncating 
every one of them on every test still will be unacceptably slow.

Hence, this plugin.
