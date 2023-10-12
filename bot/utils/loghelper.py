import logging
from logging.handlers import TimedRotatingFileHandler

rotatingFileHandler = TimedRotatingFileHandler(filename="./logs/boxbot.log", when="midnight")

def getLogger(name:str) -> logging.Logger:
  logger = logging.getLogger(name)
  logger.addHandler(rotatingFileHandler)
  return logger

def setup_logging(level:str) -> None:
  root_logger = logging.getLogger()
  rotatingFileHandler.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  root_logger.addHandler(rotatingFileHandler)
  root_logger.setLevel(level)
  root_logger