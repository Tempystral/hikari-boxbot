from abc import ABC, abstractmethod
from re import Match
from typing import Iterable, Optional

from aiohttp import ClientSession

from sauce.response import SauceResponse


class Ladle(ABC):
  '''
  A base class for image extractors, aka "ladles"
  '''
  pattern: str

  @abstractmethod
  def extract(self, match:Match, session:ClientSession) -> SauceResponse:
    pass

  def findall(self, string:str) -> Iterable[Match]:
    return list(self.pattern.finditer(string))
  
  @abstractmethod
  def cleanup(self, match:Match) -> None:
    pass

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