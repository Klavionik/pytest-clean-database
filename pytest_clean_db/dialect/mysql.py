from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_clean_db.connection import Connection

CREATE_DIRTY_TABLE = """\
CREATE TABLE __dirty_tables AS
  SELECT TABLE_NAME AS name, FALSE AS is_dirty
  FROM information_schema.tables
  WHERE table_schema = (SELECT DATABASE()) AND table_name != '__dirty_tables';
"""

CREATE_MARK_DIRTY_TRIGGER = """\
CREATE TRIGGER mark_dirty_%(table)s
AFTER INSERT ON %(table)s
FOR EACH ROW CALL mark_dirty('%(table)s');
"""

CREATE_MARK_DIRTY_FUNCTION = """\
CREATE PROCEDURE mark_dirty(IN tablename TEXT)
BEGIN
  UPDATE __dirty_tables SET is_dirty = TRUE WHERE name = tablename AND is_dirty = FALSE;
END;
"""

CREATE_CLEAN_TABLES_FUNCTION = """\
CREATE PROCEDURE clean_tables()
BEGIN
DECLARE tablename TEXT;
DECLARE done BOOL;
DECLARE cur CURSOR FOR SELECT name FROM __dirty_tables WHERE is_dirty IS TRUE;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
OPEN cur;

read_loop: LOOP
    FETCH cur INTO tablename;

    IF done THEN
        LEAVE read_loop;
    END IF;

    SET @query = CONCAT('TRUNCATE TABLE ', tablename);
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
  END LOOP;

UPDATE __dirty_tables SET is_dirty = FALSE;
END;
"""

CREATE_TRIGGERS_FUNCTION = """\
CREATE PROCEDURE create_mark_dirty_triggers()
BEGIN
DECLARE tablename TEXT;
DECLARE done BOOL;
DECLARE cur CURSOR FOR SELECT name FROM __dirty_tables;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
OPEN cur;

read_loop: LOOP
    FETCH cur INTO tablename;

    IF done THEN
        LEAVE read_loop;
    END IF;

    SET @query = CONCAT('CREATE TRIGGER mark_dirty_', tablename, ' AFTER INSERT ON ', tablename, ' FOR EACH ROW CALL mark_dirty(\'', tablename, '\');');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
  END LOOP;

UPDATE __dirty_tables SET is_dirty = FALSE;
END;
"""

SELECT_DIRTY_TABLES_NAMES = """\
SELECT name FROM __dirty_tables
"""

EXECUTE_CLEAN_TABLES = """\
CALL clean_tables();
"""

EXECUTE_CREATE_TRIGGERS = """\
CALL create_mark_dirty_triggers();
"""


def setup_tracing(connections: Iterable["Connection"]) -> None:
    for conn in connections:
        conn.execute(CREATE_DIRTY_TABLE)
        conn.execute(CREATE_MARK_DIRTY_FUNCTION)
        conn.execute(CREATE_CLEAN_TABLES_FUNCTION)
        conn.execute(CREATE_TRIGGERS_FUNCTION)
        conn.execute(EXECUTE_CREATE_TRIGGERS)


def run_clean_tables(clean_db_connections: Iterable["Connection"]) -> None:
    for conn in clean_db_connections:
        conn.execute(EXECUTE_CLEAN_TABLES)
