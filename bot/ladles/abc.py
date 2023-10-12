from abc import ABC, abstractmethod
from re import Match
from typing import Iterable, Optional

from aiohttp import ClientSession

from bot.api.response import SauceResponse


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