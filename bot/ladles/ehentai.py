import logging
import re
from html import unescape
from re import Match
from typing import Optional

from aiohttp import ClientSession
from hikari import Color

from bot.api.response import EHGallery, SauceResponse, TokenList
from bot.api.sadpanda import SadPandaApi
from bot.ladles import Ladle
from bot.utils.constants import EHENTAI_DESC

logger = logging.getLogger("ladles.ehentai")

class EHentai(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e-|ex)hentai\.org/(?P<type>g|s)/(?P<group_1>\w+)/(?P<group_2>\w+)(-(?P<page_num>\d+))?'
    self._api: SadPandaApi | None = None

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    if not self._api:
      self._api = SadPandaApi(session)

    # site:str = match.group("site")
    gallery_type:str = match.group("type")
    page_num:Optional[int] = match.group("page_num")
    ids = match.group("group_1"), match.group("group_2")

    params = await self._resolve_params(gallery_type, ids[0], ids[1], page_num)
    gallery = await self._api.get_gallery(params["gid"], params["token"])
    
    return self._create_response(gallery)
  
  def _create_response(self, gallery:EHGallery):
    prefix, description = (("ex", EHENTAI_DESC)
                           if self.__is_restricted(gallery.tags)
                           else ("e-", ""))
    description += self.__tags_to_string(gallery.tags)
    
    return SauceResponse(
      title = unescape(gallery.title).replace("\n", " "),
      description = description,
      url = f"https://{prefix}hentai.org/g/{gallery.gid}/{gallery.token}/",
      images = [gallery.thumb],
      color = Color(0xedebdf),
      count = int(gallery.filecount),
      timestamp = int(gallery.posted)
    )

  async def _resolve_params(self,
                            gallery_type:str,
                            group_1:str,
                            group_2:str,
                            page_num:Optional[str] = None):
    '''Returns a tuple containing the gallery id and gallery token'''
    if gallery_type == "g":
      return TokenList(gid=int(group_1), token=group_2)

    elif gallery_type == "s":
      try:
        return await self._api.find_original_gallery(int(group_2), group_1, page_num)
      except EHentaiApiError as e:
        logger.warning(e.message)

  def __is_restricted(self, tags: list) -> bool:
    for tag in tags:
      match = re.match(r'(fe)?male:(?P<label>\w+)', tag)
      if not match:
        continue
      if match.group("label") in self._api.restricted_tags:
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