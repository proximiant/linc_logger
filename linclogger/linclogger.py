import logging
import os
from logging import WARNING as WARNING_LEVEL

from concurrent_log_handler import ConcurrentRotatingFileHandler

__version__ = '0.1.2'

FILTERED_MODULES = [
    'kafka',
    'connexion'
]


class AppFilter(logging.Filter):
    def __init__(self, modules=None, level=None):
        self.modules = modules
        self.level = level

    def filter(self, record):
        if not self.modules or not self.level:
            return True
        return not (any((record.name.startswith(module) for module in self.modules))
                    and record.levelno < self.level)


class DefaultFilter(logging.Filter):

    def filter(self, record):
        return not (any((record.name.startswith(module) for module in FILTERED_MODULES))
                    and record.levelno < WARNING_LEVEL)


class LincLogger:
    def __init__(self, service_name, config=None, log_level=None, log_filename=None, event_log_filename=None,
                 filtered_modules=None, filter_level=None, add_console_log=True):
        os.environ['SERVICE_NAME'] = service_name
        if config is not None and isinstance(config, dict):
            self.log_level = config.get("LOG_LEVEL", log_level)
            self.log_filename = config.get("LOG_FILENAME", log_filename)
            self.event_log_filename = config.get(
                "EVENT_LOG_FILENAME", event_log_filename)
            self.add_console_log = bool(config.get(
                'ADD_CONSOLE_LOG', add_console_log))
        else:
            self.log_level = log_level
            self.log_filename = log_filename
            self.event_log_filename = event_log_filename
            self.add_console_log = add_console_log

        self.log_level = self.log_level or 'INFO'
        self.log_filename = self.log_filename or 'var/log/linc_logger/%s.log' % service_name
        self.event_log_filename = self.event_log_filename or 'var/log/linc_logger/%s.event.log' % service_name
        self.service_name = service_name
        self.filtered_modules = filtered_modules
        self.filter_level = filter_level
        self.logging = {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'app_logs': {
                    '()': AppFilter,
                    'modules': self.filtered_modules,
                    'level': self.filter_level
                },
                'default': {
                    '()': DefaultFilter
                }
            },
            'formatters': {
                'general_file': {
                    '()': 'linclogger.log_formatter.LincGeneralFormatter',
                    'format': '%(asctime)%(levelname)%(name)%(funcName)%(process)%(thread)%(message)%(lineno)',
                    'datefmt': '%Y-%m-%dT%H:%M:%S.%FZ%z',
                },
                'linc_event': {
                    '()': 'linclogger.log_formatter.LincEventFormatter',
                    'format': '%(asctime)%(levelname)%(funcName)%(message)',
                    'datefmt': '%Y-%m-%dT%H:%M:%S.%FZ%z',
                },
            },
            'handlers': {
                'app_file': {
                    'level': self.log_level,
                    'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
                    'formatter': 'general_file',
                    'filename': self.log_filename,
                    'filters': ['app_logs', 'default'],
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 10,
                },
                'event_file': {
                    'level': self.log_level,
                    'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
                    'formatter': 'linc_event',
                    'filename': self.event_log_filename,
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 10,
                },
            },
            'loggers': {
                '': {
                    'handlers': ['app_file'],
                    'level': self.log_level,
                },
                'event': {
                    'handlers': ['event_file'],
                    'level': self.log_level,
                    'propagate': False,
                },
            },
        }

    def get_service_name(self):
        return self.service_name

    def get_logging_setup(self, use_console_out=False):
        log = self.logging

        if use_console_out or os.environ.get('ENV', 'dev') == 'local':
            for logger in log['loggers'].keys():
                log['loggers'][logger]['handlers'] = ['console']
            log['handlers'] = {'console': {
                'level': self.log_level, 'class': 'logging.StreamHandler'}}

        # add console logs too useful for datadog
        if self.add_console_log:
            root_logger = log['loggers']['']
            root_logger['handlers'] = root_logger['handlers'] + ['console']
            log['handlers']['console'] = {
                'level': self.log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'general_file',
                'filters': ['app_logs', 'default'],
            }
        return log
