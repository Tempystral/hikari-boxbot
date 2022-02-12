from abc import ABC, abstractmethod
from re import Pattern, Match, finditer
from typing import Dict, Iterable, Optional

import aiohttp

from sauce import SauceResponse


class Ladle(ABC):
  '''
  A base class for image extractors, aka "ladles"
  '''
  pattern: str

  @abstractmethod
  def extract(self, match:Match, session:aiohttp.ClientSession) -> SauceResponse:
    pass

  def findall(self, string:str) -> Iterable[Match]:
    return list(self.pattern.finditer(string))

class LadleException(Exception):
  """
  A base exception for ladles to extend.
  """
  def __init__(self, code:Optional[str] = None,
                     message:Optional[str] = None,
                     data:Optional[dict] = None):
    self.code = code
    self.message = message
    self.data = data