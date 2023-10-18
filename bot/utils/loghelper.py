import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def __create_log_dir(path:str):
  logfile = Path(path)
  logfile.parent.mkdir(parents=True, exist_ok=True)
  logfile.touch()

def setup_logging(level:str, logpath:str) -> None:
  
  __create_log_dir(logpath)

  rotatingFileHandler = TimedRotatingFileHandler(filename=logpath, when="midnight")

  root_logger = logging.getLogger()
  rotatingFileHandler.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  root_logger.addHandler(rotatingFileHandler)
  root_logger.setLevel(level)
  
  logging.getLogger("hikari.gateway").setLevel(logging.WARN)
  logging.getLogger("hikari.ratelimits").setLevel(logging.INFO)