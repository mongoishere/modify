import sys, logging
from logging import DEBUG, INFO, ERROR

class Logger(object):

    def __init__(self, name, frmt="%(asctime)s | %(levelname)s | %(message)s", dmt="%Y-%m-%d %H:%M:%S", level=DEBUG):

        self.logger = logging.getLogger(name)
        formatter = logging.Formatter(frmt, dmt)
        file_handler = logging.FileHandler(f"{name}.log", mode='a')
        file_handler.setFormatter(formatter)

        #Config logger attributes
        self.logger.setLevel(level)
        self.logger.addHandler(file_handler)
    
    def info(self, msg, extra=None):
        self.logger.info(msg, extra=extra)

    def error(self, msg, extra=None):
        self.logger.error(msg, extra=extra)

    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra=extra)