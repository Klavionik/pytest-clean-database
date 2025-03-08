from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_clean_db.connection import Connection

CREATE_DIRTY_TABLE = """\
CREATE TABLE %(schema)s.__dirty_tables (name, is_dirty) AS (
  SELECT relname, FALSE
  FROM pg_class
  WHERE relkind = 'r'
  AND relnamespace = '%(schema)s'::regnamespace
)
"""

CREATE_MARK_DIRTY_FUNCTION = """\
CREATE FUNCTION %(schema)s.mark_dirty()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$func$
BEGIN
  UPDATE %(schema)s.__dirty_tables SET is_dirty = TRUE WHERE name = TG_TABLE_NAME;
  RETURN NEW;
END;
$func$;
"""

CREATE_CLEAN_TABLES_FUNCTION = """\
CREATE FUNCTION %(schema)s.clean_tables()
  RETURNS void
  LANGUAGE plpgsql
AS
$func$
DECLARE table_name text;
BEGIN
  FOR table_name in
    SELECT name
    FROM %(schema)s.__dirty_tables
    WHERE is_dirty IS TRUE
  LOOP
    EXECUTE format('TRUNCATE TABLE %(schema)s.%%I RESTART IDENTITY CASCADE', table_name);
  END LOOP;
  UPDATE %(schema)s.__dirty_tables SET is_dirty = FALSE;
END;
$func$;
"""

CREATE_TRIGGERS_FUNCTION = """\
CREATE FUNCTION %(schema)s.create_mark_dirty_triggers()
  RETURNS void
  LANGUAGE plpgsql
AS
$func$
DECLARE table_name text;
BEGIN
  FOR table_name in
    SELECT name
    FROM %(schema)s.__dirty_tables
  LOOP
    EXECUTE format('CREATE TRIGGER mark_dirty AFTER INSERT ON %(schema)s.%%I EXECUTE FUNCTION %(schema)s.mark_dirty();', table_name);
  END LOOP;
END;
$func$;
"""

EXECUTE_CLEAN_TABLES = """\
SELECT %(schema)s.clean_tables();
"""

EXECUTE_CREATE_TRIGGERS = """\
SELECT %(schema)s.create_mark_dirty_triggers();
"""


def setup_tracing(db_schema: str, conn: "Connection") -> None:
    conn.execute(CREATE_DIRTY_TABLE % {"schema": db_schema})
    conn.execute(CREATE_MARK_DIRTY_FUNCTION % {"schema": db_schema})
    conn.execute(CREATE_CLEAN_TABLES_FUNCTION % {"schema": db_schema})
    conn.execute(CREATE_TRIGGERS_FUNCTION % {"schema": db_schema})
    conn.execute(EXECUTE_CREATE_TRIGGERS % {"schema": db_schema})


def run_clean_tables(db_schema: str, conn: "Connection") -> None:
    conn.execute(EXECUTE_CLEAN_TABLES % {"schema": db_schema})
