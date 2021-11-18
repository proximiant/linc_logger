import logging
import unittest
from logging.config import dictConfig

from linclogger.linclogger import LincLogger


class TestLogger(unittest.TestCase):


    def test_logger(self):

        log = logging.getLogger("test")
        linc_logger = LincLogger('test')
        dictConfig(linc_logger.get_logging_setup())
        
        log.info("this is a test")

if __name__ == '__main__':
    unittest.main()
