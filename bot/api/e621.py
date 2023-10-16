import asyncio
import json
import logging
from collections import deque
from time import time

import dacite
from aiohttp import BasicAuth, ClientSession
from decouple import config

from bot.api.exception import LadleException
from bot.api.response import eSixPoolResponse, eSixPostResponse

logger = logging.getLogger("bot.api.e621")

class ESixApi:
  def __init__(self, session:ClientSession|None = None):
    self._auth = BasicAuth(
      config("E621_USER", cast=str),
      config("E621_KEY", cast=str)
    )
    self._base_url = 'https://e621.net'
    self._session = session
    self._prev_requests: deque[float] = deque(maxlen=2)

  @property
  def session(self):
    return self._session

  @session.setter
  def session(self, session: ClientSession):
    self._session = session

  async def __get(self, url: str, params: dict = {}) -> dict:
    await self.__dyn_rate_limit(time())

    req_url = self._base_url + url
    async with self.session.get(req_url, params=params, headers={'User-Agent': 'Sauce/2.0'}, auth=self._auth) as response:
      try:
        result = json.loads(await response.read())
        assert isinstance(result, dict)
      except AssertionError | json.JSONDecodeError as ae:
        raise EsixApiException(message="Response is not in json format", reason=ae.__str__(), data=result)
      if result.get("success"):
        response_code = result["code"] if "code" in result else -1
        raise EsixApiException(code=response_code, reason=result["reason"], data=result)
    
    return result
  
  async def get_pool(self, id: int) -> eSixPoolResponse:
    response = await self.__get(f'/pools/{id}.json')
    return eSixPoolResponse(**response)

  async def get_post(self, id: int):
    response = await self.__get(f'/posts/{id}.json')
    return dacite.from_dict(data_class=eSixPostResponse, data=response["post"])

  async def get_posts(self, ids: list[int]):
    tags = [f"id:{','.join(str(id) for id in ids)}", "order:id_desc"]
    params = { "tags": "+".join(tags) }
    response = await self.__get(f'/posts.json', params=params)
    return [dacite.from_dict(data_class=eSixPostResponse, data=post) for post in response["posts"]]

  def __count_request(self, t: float):
    self._prev_requests.appendleft(t)
  
  def __check_time(self, t: float):
    if len(self._prev_requests) < 1:
      return self._prev_requests[1] - t < 1, self._prev_requests[1]
    return False, 1.

  async def __dyn_rate_limit(self, t: float):
    must_wait, delta = self.__check_time(t)
    if must_wait:
      await asyncio.sleep(1 - delta)
    self.__count_request(t)

class EsixApiException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from e621.net
  """