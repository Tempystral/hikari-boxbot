from html import unescape

from re import Match
import re
from typing import Optional, Tuple

import json
from aiohttp import ClientSession
from hikari import Color
from scalpl import Cut

from utils.constants import EHENTAI_DESC, RESTRICTED_TAGS
from bot.api.response import SauceResponse

from . import Ladle

import logging
logger = logging.getLogger("ladles.ehentai")

class EHentai(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e-|ex)hentai\.org/(?P<type>g|s)/(?P<group_1>\w+)/(?P<group_2>\w+)(-(?P<page_num>\d+))?'
    self._request_url = 'https://api.e-hentai.org/api.php'
    self._restricted_tags = RESTRICTED_TAGS

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    gallery_id:int = None
    gallery_token:str = None
    # try:
    site:str = match.group("site")
    gallery_type:str = match.group("type")
    page_num:Optional[int] = match.group("page_num")
    # except AttributeError as e:
    #   logger.warning(f"Ladle triggered, but match was invalid. Input: {match[0]}")
    #   return None

    gallery_id, gallery_token = await self._retrieve_gallery_details(session, gallery_type, match.group("group_1"), match.group("group_2"), page_num)
      
    # Good response: {'gmetadata': [{'gid': 1234567, 'token': '0asfh80qw8', 'archiver_key': etc... ]}]}
    # Bad response:  {'gmetadata': [{'gid': 1234567, 'error': 'Key missing, or incorrect key provided.'}]}
    params = {
      "method" : "gdata",
      "gidlist" : [[gallery_id, gallery_token]],
      "namespace" : 1
    }
    data:dict = await self._get_gallery_metadata(params, session)
    
    metadata = Cut(data["gmetadata"][0]) # This will only work for single requests. This logic will need to change to accomodate multi-gallery requests
    if "error" in metadata:
      logger.warning(f'E-Hentai API error: {metadata["error"]}')
    
    response = self._create_response(metadata, gallery_id, gallery_token)
    return response
  
  def _create_response(self, metadata:Cut, gallery_id:int, gallery_token:str) -> SauceResponse:
    tags = metadata.get("tags")
    prefix, description = (("ex", EHENTAI_DESC)
                           if self.__is_restricted(tags)
                           else ("e-", ""))
    description += self.__tags_to_string(tags)
    
    return SauceResponse(
      title = unescape(metadata.get("title")).replace("\n", " "),
      description = description,
      url = f"https://{prefix}hentai.org/g/{gallery_id}/{gallery_token}/",
      image = metadata.get("thumb"),
      color = Color(0xedebdf),
      count = int(metadata.get("filecount"))
    )

  async def _get_gallery_metadata(self, params:dict, session:ClientSession) -> Optional[dict]:
    async with session.post(self._request_url, json=params, headers={'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      if "error" in data:
        raise EHMetadataError(f'E-Hentai API error: {data["error"]}')
      return data

  async def _retrieve_gallery_details(self,session:ClientSession,
                                      gallery_type:str,
                                      group_1:str,
                                      group_2:str,
                                      page_num:Optional[str] = None) -> Tuple[str, str]:
    if gallery_type == "s":
      gallery_id = int(group_2)
      page_token = group_1
      try:
        gallery_token = await self._retrieve_gallery_token(page_token, gallery_id, page_num, session)
      except EHentaiApiError as e:
        logger.warning(e.message)

    elif gallery_type == "g":
      gallery_id = int(group_1)
      gallery_token = group_2
    
    return gallery_id, gallery_token

  async def _retrieve_gallery_token(self, page_token: str, gallery_id: int, page_num: int, session: ClientSession) -> str:
    if page_num == None:
      raise EHGalleryTokenError(f'Gallery token requested for page, but no page number was included.')
    # Good response: {'tokenlist': [{'gid': 1234567, 'token': 'aw3o8fja83'}]}
    # Bad response:  {'tokenlist': [{'gid': 1136045, 'error': 'invalid or malformed arguments'}]}
    params = {
      "method": "gtoken",
      "pagelist": [[gallery_id, page_token, page_num]]
    }
    async with session.post(self._request_url, json = params, headers = {'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      gdata = data["tokenlist"][0]
      if "error" in gdata:
        raise EHGalleryTokenError(f'E-Hentai API error: {gdata["error"]}')
      else:
        logger.debug(f"Retrieved token for gallery {gallery_id}: {gdata['token']}")
        return gdata["token"]

  def __is_restricted(self, tags: list) -> bool:
    for tag in tags:
      match = re.match(r'(fe)?male:(?P<label>\w+)', tag)
      if not match:
        continue
      if match.group("label") in self._restricted_tags:
        return True
    return False
  
  def __tags_to_string(self, tags: list) -> str:
    s = "Tags: "
    for tag in tags:
      trunc = tag.split(":")[-1]
      s += f"{trunc}, "
    return s[:-2] # Remove trailing space and comma

  async def cleanup(self, match:Match) -> None:
    pass

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