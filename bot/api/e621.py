import json
from aiohttp import BasicAuth, ClientSession
from decouple import config

import asyncio

from .exception import LadleException
from .response import eSixPoolResponse

class ESixApi:
  def __init__(self, session:ClientSession|None = None):
    self._auth = BasicAuth(
      config("E621_USER", cast=str),
      config("E621_KEY", cast=str)
    )
    self._base_url = 'https://e621.net'
    self._request_count = 0
    self.sleep_timer = 0
    self._session = session

  @property
  def session(self):
    return self._session

  @session.setter
  def session(self, session: ClientSession):
    self._session = session

  async def __get(self, url: str) -> dict:
    await asyncio.sleep(self.sleep_timer)
    req_url = self._base_url + url
    async with self.session.get(req_url, headers={'User-Agent': 'Sauce/2.0'}, auth=self._auth) as response:
      try:
        result = json.loads(await response.read())
        assert isinstance(result, dict)
      except AssertionError | json.JSONDecodeError as ae:
        raise EsixApiException(message="Response is not in json format", reason=ae.__str__(), data=result)
      if result.get("success"):
        response_code = result["code"] if "code" in result else -1
        raise EsixApiException(code=response_code, reason=result["reason"], data=result)

    self.sleep_timer = 0.5
    return result
  
  async def get_pool(self, id: int) -> eSixPoolResponse:
    response = await self.__get(f'/pools/{id}.json')
    return eSixPoolResponse(**response)

  async def get_post(self, id: int):
    # response = await self.__get(f'/posts/{id}.json')
    pass

  async def get_posts(self, ids: list[int]):
    pass


class EsixApiException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from e621.net
  """