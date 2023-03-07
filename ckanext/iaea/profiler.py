from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging
import traceback
import json
import os
from Queue import Queue
from threading import Thread, Event

logger = logging.getLogger("profiler.sqlalchemy")
logger.setLevel(logging.DEBUG)


def truncate(stmt, max_chars=50):
    if not stmt or len(stmt) <= max_chars:
        return stmt
    return stmt[0:max_chars] + '...'


class ProfilerOutput:

    def __init__(self, out_file_name, trace_enabled=False):
        self.out_file_name = out_file_name
        self.trace_enabled = trace_enabled
        self.q = Queue()
        Thread(target=self._write_and_flush).start()

    def mark_query_end(self, statement, exec_time):
        logline = {
            'query': statement,
            'exec_time': exec_time,
        }
        if self.trace_enabled:
            logline['trace'] = traceback.format_stack()
        trace_line = '{}\n'.format(
            json.dumps(logline)
        )
        self.q.put_nowait(trace_line)

    def _write_and_flush(self):
        while True:
            buff = []
            if self.q.empty():
                time.sleep(0.1)
            while not self.q.empty():
                line = self.q.get(timeout=0.1)
                if not line:
                    break
                buff.append(line)
                if len(buff) >= 1000:
                    break
            if buff:
                with open(self.out_file_name, 'a') as f:
                    f.write(''.join(buff))


def setup_query_profiler():

    out_file = os.getenv('CKAN_QUERY_PROFILER_OUT_FILE') or '/tmp/queries.log'
    profiler = ProfilerOutput(out_file, trace_enabled=True)
    logger.info('Query output file: {}'.format(out_file))

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        profiler.mark_query_end(statement, total)

    logger.info('Query profiler set up.')
