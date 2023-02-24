from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logger = logging.getLogger("profiler.sqlalchemy")
logger.setLevel(logging.DEBUG)


def truncate(stmt, max_chars=50):
    if not stmt or len(stmt) <= max_chars:
        return stmt
    return stmt[0:max_chars] + '...'

def setup_query_profiler():

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Total Time: %fs; statement: %s", total, truncate(statement))

    logger.info('*** Query profiler set up ***')