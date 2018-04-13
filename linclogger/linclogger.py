import logging
import os
from cloghandler import ConcurrentRotatingFileHandler
from logging import WARNING as WARNING_LEVEL

__version__ = '0.0.3'

FILTERED_MODULES = (
  'kafka'
  'connexion'
)


class AppFilter(logging.Filter):
    def filter(self, record):
        return not (any((record.name.startswith(module) for module in FILTERED_MODULES)) and record.levelno < WARNING_LEVEL)


class LincLogger():
    def __init__(self, service_name, config=None, log_level=None, log_filename=None, event_log_filename=None):
        os.environ['SERVICE_NAME'] = service_name
        if config is not None and isinstance(config, dict):
            self.log_level = config.get("LOG_LEVEL", log_level)
            self.log_filename = config.get("LOG_FILENAME", log_filename)
            self.event_log_filename = config.get("EVENT_LOG_FILENAME", event_log_filename)
        else: 
            self.log_level = log_level
            self.log_filename = log_filename
            self.event_log_filename = event_log_filename

        self.log_level = self.log_level or 'INFO'
        self.log_filename = self.log_filename or 'var/log/linc_logger/%s.log' % service_name
        self.event_log_filename = self.event_log_filename or 'var/log/linc_logger/%s.event.log' % service_name
        self.service_name = service_name

        self.logging = {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'app_logs': {
                    '()': AppFilter
                }
            },
            'formatters': {
                'general_file': {
                    '()': 'linclogger.log_formatter.LincGeneralFormatter',
                    'format': '%(asctime)%(levelname)%(name)%(funcName)%(process)%(thread)%(message)%(lineno)'
                },
                'linc_event': {
                    '()': 'linclogger.log_formatter.LincEventFormatter',
                    'format': '%(asctime)%(levelname)%(funcName)%(message)'

                },
            },
            'handlers': {
                'app_file': {
                    'level': self.log_level,
                    'class': 'cloghandler.ConcurrentRotatingFileHandler',
                    'formatter': 'general_file',
                    'filename': self.log_filename,
                    'filters': ['app_logs'],
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 10,
                },
                'event_file': {
                    'level': self.log_level,
                    'class': 'cloghandler.ConcurrentRotatingFileHandler',
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
                },
            },
        }

    def get_service_name(self):
        return self.service_name

    def get_logging_setup(self):
        log = self.logging
        if os.environ.get('ENV', 'dev') == 'local':
            for logger in log['loggers'].keys():
                log['loggers'][logger]['handlers'] = ['console']
            log['handlers'] = {'console': {'level': self.log_level, 'class': 'logging.StreamHandler'}}
        return log  




