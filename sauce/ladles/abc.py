from abc import ABC, abstractmethod
from re import Pattern, Match, finditer
from typing import Dict, Iterable

import aiohttp

from sauce import SauceResponse


class Ladle(ABC):
  '''
  A base class for image extractors, aka "ladles"
  '''
  pattern: Pattern

  @abstractmethod
  def extract(self, match:Match, session:aiohttp.ClientSession) -> SauceResponse:
    pass

  def findall(self, string:str) -> Iterable[Match]:
    return list(self.pattern.finditer(string))
