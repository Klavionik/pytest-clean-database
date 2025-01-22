CREATE_DIRTY_TABLE = """\
CREATE TABLE __dirty_tables (name, is_dirty) AS (
  SELECT relname, FALSE
  FROM pg_class
  WHERE relkind = 'r'
  AND relnamespace = 'public'::regnamespace
)
    """

CREATE_MARK_DIRTY_FUNCTION = """\
CREATE FUNCTION mark_dirty()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$func$
BEGIN
  UPDATE __dirty_tables SET is_dirty = TRUE WHERE name = TG_TABLE_NAME;
  RETURN NEW;
END;
$func$;
"""

CREATE_MARK_DIRTY_TRIGGER = """\
CREATE TRIGGER mark_dirty
AFTER INSERT ON %s
EXECUTE FUNCTION mark_dirty();
"""

CREATE_CLEAN_TABLES_FUNCTION = """\
CREATE FUNCTION clean_tables()
  RETURNS void
  LANGUAGE plpgsql
AS
$func$
DECLARE table_name text;
BEGIN
  FOR table_name in
    SELECT name
    FROM __dirty_tables
    WHERE is_dirty IS TRUE
  LOOP
    EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', table_name);
  END LOOP;
  UPDATE __dirty_tables SET is_dirty = FALSE;
END;
$func$;
"""

SELECT_DIRTY_TABLES_NAMES = """\
SELECT name FROM __dirty_tables
"""

EXECUTE_CLEAN_TABLES = """\
SELECT clean_tables();
"""
