import json
from typing import Optional

from aiohttp import ClientSession
from bot.api.response import EHResponse
from bot.utils.constants import RESTRICTED_TAGS
from dacite import from_dict


class SadPandaApi:
  def __init__(self, session:ClientSession) -> None:
    self._request_url = 'https://api.e-hentai.org/api.php'
    self._restricted_tags = RESTRICTED_TAGS
    self._session = session
  
  async def get_gallery(self, gallery_id:int, gallery_token:str):
    # Good response: {'gmetadata': [{'gid': 1234567, 'token': '0asfh80qw8', 'archiver_key': etc... ]}]}
    # Bad response:  {'gmetadata': [{'gid': 1234567, 'error': 'Key missing, or incorrect key provided.'}]}
    params = {
      "method" : "gdata",
      "gidlist" : [[gallery_id, gallery_token]],
      "namespace" : 1
    }
    data = await self._get(params, self._session)
  
  async def _get(self, params:dict, session:ClientSession):
    async with session.post(self._request_url, json=params, headers={'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      if self.__error_in_response(data):
        raise EHMetadataError(f'E-Hentai API error: {data["error"]}')
      # TODO If you request multiple galleries and one of them errors out, this becomes a problem
      # It's fine for now since my use case is only ever single-gallery lookups
      return [ from_dict(data_class=EHResponse, data=gallery) for gallery in data["gmetadata"] ]
    
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