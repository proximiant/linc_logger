import logging
import unittest
from logging.config import dictConfig

from linclogger.linclogger import LincLogger


class TestLogger(unittest.TestCase):
    def test_logger(self):

        log = logging.getLogger("test")
        linc_logger = LincLogger("test service")
        dictConfig(linc_logger.get_logging_setup())

        log.info("this is a test")

    def test_event_logger(self):

        log = logging.getLogger("event")
        linc_logger = LincLogger("test service")
        dictConfig(linc_logger.get_logging_setup())

        event = {
            "category": "category",
            "action": "action",
            "event": {
                "franchise_id": 123,
                "bot_user_id": 456,
                "channel": 789,
            },
        }
        log.info(event)


if __name__ == "__main__":
    unittest.main()
