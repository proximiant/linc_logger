import logging, os
import logmatic
from logging import WARNING as WARNING_LEVEL

__version__ = '0.0.1'

FILTERED_MODULES = (
  'kafka'
  'connexion'
)


class AppFilter(logging.Filter):
    def filter(self, record):
        return not (any((record.name.startswith(module) for module in FILTERED_MODULES)) and record.levelno < WARNING_LEVEL)


class LincLogger():
    def __init__(self, service_name, config=None,log_level=None, log_filname=None, event_log_filname=None):
        if config is not None and isinstance(config, dict):
            self.log_level = config.get("LOG_LEVEL", log_level)
            self.log_filename = config.get("LOG_FILENAME", log_filname)
            self.event_log_filname = config.get("EVENT_LOG_FILENAME", event_log_filname)
        else: 
            self.log_level = log_level
            self.log_filname = log_filname
            self.event_log_filname = event_log_filname

        self.log_level = self.log_level or 'INFO'
        self.log_filename = self.log_level or 'var/log/linc_logger/err.log'
        self.event_log_filname = self.log_filname or 'var/log/linc_logger/event.log'
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
                    'format': '%(asctime)%(levelname)%(name)%(funcName)%(process)%(thread)%(message)'
                },
                'linc_event': {
                    '()': 'linclogger.log_formatter.LincEventFormatter',
                    'format': '%(asctime)%(levelname)%(funcName)%(message)'

                },
            },
            'handlers': {
                'console': {
                    'level': self.log_level,
                    'class': 'logging.StreamHandler',
                },
                'app_file': {
                    'level': self.log_level,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'general_file',
                    'filename': self.log_filename,
                    'filters' : ['app_logs'],
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 10,
                },
                'event_file': {
                    'level': self.log_level,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'linc_event',
                    'filename': self.event_log_filname,
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 10,
                },
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'app_file'],
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
        if os.environ.get('ENV', 'local') == 'local':
            for logger in log['loggers'].keys():
                log['loggers'][logger]['handlers'] = ['console']
            log['handlers'] = {'console': {'level': self.log_level, 'class': 'logging.StreamHandler'}}
        return log  




