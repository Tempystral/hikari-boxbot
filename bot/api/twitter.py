import json
import logging

import dacite
from aiohttp import ClientSession

from bot.api.exception import LadleException
from bot.api.response.twitter import (FXTwitterResponse, Tweet,
                                      VXTwitterResponse)

logger = logging.getLogger("bot.api.e621")

class TwitterAPI:
  def __init__(self, session:ClientSession|None = None):
    self._session = session

  @property
  def session(self):
    return self._session

  @session.setter
  def session(self, session: ClientSession):
    self._session = session

  async def __get(self, client:str, user:str, id:str):
    response = await self._session.get(f"https://api.{client}twitter.com/{user}/status/{id}/")
    if response.status != 200:
      raise StatusException
    return json.loads(await response.text())

  async def __get_fx(self, user:str, id:str):
    data = await self.__get("fx", user, id)
    response = dacite.from_dict(data_class=FXTwitterResponse, data=data)
    if (response.code != 200):
      raise FXTwitterException
    else:
      return response
  
  async def __get_vx(self, user:str, id:str):
    try:
      data = await self.__get("vx", user, id)
      return dacite.from_dict(data_class=VXTwitterResponse, data=data)
    except StatusException:
      raise VXTwitterException

  def __build_response(self, data):
    return data

  async def get_tweet(self, user: str, id: str):
    data = None
    try:
      data = await self.__get_fx(user, id)
      return self.__build_response(data)
    except FXTwitterException:
      logger.warn("Could not retrieve tweet with FXTwitter!")
    
    try:
      data = await self.__get_vx(user, id)
      return self.__build_response(data)
    except VXTwitterException:
      logger.warn("Couldn't get tweet data from backup VXTwitter!")
    return data
    
class StatusException(BaseException):
  pass    

class FXTwitterException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from FXTwitter
  """

class VXTwitterException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from VXTwitter
  """