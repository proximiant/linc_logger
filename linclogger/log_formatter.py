"""
This module defines linc general log formatter for application logs.
New fields: error code, function name, process id, thread id.
"""

import logging, socket, os
from logmatic import JsonFormatter
from logging import Formatter
import json

import zlib

log = logging.getLogger(__name__)
SERVICE = os.environ.get("SERVICE_NAME")


class LincGeneralFormatter(JsonFormatter):

    def process_log_record(self, log_record):
        # Enforce the presence of a timestamp
        if "asctime" in log_record:
            log_record["timestamp"] = log_record["asctime"]
            del log_record["asctime"]
        else:
            log_record["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ%z")

        if self._extra is not None:
            for key, value in self._extra.items():
                print (value)
                log_record[key] = value
        errno = None
        if log_record['levelname'] in (logging.ERROR, logging.CRITICAL):
            try:
                errno = zlib.adler32(log_record['message'])
            except zlib.error:
                log.warn('Zlib cant calculate format string: %s checksum', log_record['message'])
            except Exception as e:
                log.warn('Fails to generate errno: %s', e)
        log_record['errno'] = errno if errno is not None else ''
        log_record = self.transform_logs(log_record)
        return super(JsonFormatter, self).process_log_record(log_record)

    def transform_logs(self, log_record):
        if 'funcName' in log_record:
            log_record['functioname'] = log_record['funcName']
            del log_record['funcName']
        if 'name' in log_record:
            log_record['module'] = log_record['name']
            del log_record['name']
        if 'message' in log_record:
            log_record['msg'] = log_record['message']
            del log_record['message']
        else:
            log_record['msg'] = ''
        if 'levelname' in log_record:
            log_record['loglevel'] = log_record['levelname']
            del log_record['levelname']
        log_record['type'] = SERVICE + '-app-syslog'
        log_record['hostname'] = socket.gethostname()
        return log_record

"""
This module defines Linc event log formatter for event logs.
Typical usage: event_logger.info(category, action, event_dict)
"""

class LincEventFormatter(JsonFormatter):
    """
    Linc event formatter
    """

    def process_log_record(self, log_record):
        required_fields = {
            'category': 'category is required',
            'action': 'action is required'
        }
        # Enforce the presence of a timestamp
        if "asctime" in log_record:
            log_record["timestamp"] = log_record["asctime"]
            del log_record["asctime"]
        else:
            log_record["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ%z")
        if 'funcName' in log_record:
            log_record['functioname'] = log_record['funcName']
            del log_record['funcName']
        log_record['type'] = SERVICE + '-event-log'
        for field in required_fields:
            if field not in log_record:
                log.exception("Field %s" % (required_fields[field]))
                raise Exception(required_fields[field])
        return super(JsonFormatter, self).process_log_record(log_record)