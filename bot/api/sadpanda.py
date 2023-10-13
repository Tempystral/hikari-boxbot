import json
import logging

from aiohttp import ClientSession
from bot.api.response import EHCategory, EHGalleryResponse, TokenList
from bot.utils.constants import RESTRICTED_TAGS
from dacite import Config, from_dict

logger = logging.getLogger("bot.api.sadpanda")

class SadPandaApi:
  def __init__(self, session:ClientSession) -> None:
    self._request_url = 'https://api.e-hentai.org/api.php'
    self.restricted_tags = RESTRICTED_TAGS
    self._session = session
  
  async def get_gallery(self, gallery_id:int, gallery_token:str):
    params = {
      "method" : "gdata",
      "gidlist" : [[gallery_id, gallery_token]],
      "namespace" : 1
    }
    data = await self._get(params, self._session)
    gallery = from_dict(data_class=EHGalleryResponse, data=data, config=Config(cast=[EHCategory]))
    return gallery.gmetadata[0]
  
  async def find_original_gallery(self, gallery_id:int, page_token:str, page_num:int):
    params = {
      "method": "gtoken",
      "pagelist": [[gallery_id, page_token, page_num]]
    }
    data = await self._get(params, self._session)
    return TokenList(**data["tokenlist"][0])

  async def _get(self, params:dict, session:ClientSession):
    async with session.post(self._request_url, json=params, headers={'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      if self.__error_in_response(data):
        raise EHMetadataError(f'E-Hentai API error: {data["error"]}')
      # TODO If you request multiple galleries and one of them errors out, this becomes a problem
      # It's fine for now since my use case is only ever single-gallery lookups
      return data
    
  def __error_in_response(self, data:dict[str, str]):
    if "error" in data:
      return data["error"]
    elif "gmetadata" in data and "error" in data["gmetadata"]:
      return data["gmetadata"]["error"]
    else:
      return None

class EHentaiApiError(ValueError):
  def __init__(self, message):
    super().__init__(message)
    self.message = message

class EHGalleryTokenError(EHentaiApiError):
  def __init__(self, message):
    super().__init__(message)
    self.message = message

class EHMetadataError(EHentaiApiError):
  def __init__(self, message):
    super().__init__(message)
    self.message = message