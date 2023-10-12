import json
from aiohttp import BasicAuth, ClientSession
from decouple import config

import asyncio

from .exception import LadleException

class ESixApi:
  def __init__(self):
    self._auth = BasicAuth(
      config("E621_USER", cast=str),
      config("E621_KEY", cast=str)
    )
    self._base_url = 'https://e621.net'
    self._request_count = 0
    self.sleep_timer = 0

  async def get(self, url: str, session: ClientSession) -> dict:
    await asyncio.sleep(self.sleep_timer)
    req_url = self._base_url + url
    async with session.get(req_url, headers={'User-Agent': 'sauce/0.1'}, auth=self._auth) as response:
      text = await response.read()
      result:dict = json.loads(text)
      #logger.debug(result)
      if result.get("success"):
        raise EsixApiException(code=result["code"], message=result["message"], data=result)

    self.sleep_timer = 0.5
    return result
  
class EsixApiException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from e621.net
  """