import logging
import os
from io import BytesIO
from re import Match
from typing import Dict, Optional

import aiohttp
from decouple import config
from hikari import Color
from pixivpy_async import AppPixivAPI
from pixivpy_async.utils import JsonDict
from sauce import SauceResponse
from utils import pixiv_auth
from utils.mlstripper import strip_tags
from utils.py_ugoira import convert_ugoira_frames, get_ugoira_frames

from . import Ladle

logger = logging.getLogger("ladles.pixiv")

_REQUESTS_KWARGS = {'verify': False}

class Pixiv(Ladle):
  def __init__(self):
    self.illust_pattern = r'https?://www\.pixiv\.net/[a-z]+/artworks/(?P<id1>\d+)'
    self.direct_pattern = r'https?://i\.pximg\.net/\S+/(?P<id2>\d+)_p(?P<page>\d+)(?:_\w+)?\.\w+'
    self.pattern = self.direct_pattern + '|' + self.illust_pattern
    self.hotlinking_allowed = False

  async def extract(self, match:Match, session: aiohttp.ClientSession) -> SauceResponse:
    api = AppPixivAPI(proxy="socks5://127.0.0.1:8080", client=session)
    await api.login(refresh_token=pixiv_auth.refresh(config("PIXIV_REFRESH_TOKEN")))

    if match.group("id1"):
      return await self.extract_illust(match.group("id1"), api, session)
    else:
      return await self.extract_illust(match.group('id2'), api, session)

  async def extract_illust(self, id:int, api:AppPixivAPI, session: aiohttp.ClientSession) -> SauceResponse:
    illust_id = id
    details:JsonDict = await api.illust_detail(illust_id)
    logger.debug(details)

    if 'illust' not in details:
      return

    images = None
    image = None
    video = None
    page_count = details.illust.page_count

    if details.illust.type == "ugoira":
      video = await self._process_ugoira_video(details.illust.id, api)
    else:
      if self._safe_for_work(details):
        if page_count > 1:
          images = [await self.download(i.image_urls.original, session) for i in details.illust.meta_pages[1:]]
      else:
        if page_count == 1:
          image = await self.download(details.illust.meta_single_page.original_image_url, session)
        else:
          images = [await self.download(i.image_urls.original, session) for i in details.illust.meta_pages]
          logger.debug(images)
    
    response = SauceResponse(
      title = details.illust.title,
      description = strip_tags(details.illust.caption),
      url = 'https://www.pixiv.net/en/artworks/' + illust_id,
      images = images,
      image = image,
      video = video,
      author_name = details.illust.user.name,
      author_icon = await self.download(self._get_author_icon(details), session),
      author_url = f"https://www.pixiv.net/en/users/{details.illust.user.id}",
      color = Color(0x0096fa)
    )
    return response

  @staticmethod
  async def download(url: str, session: aiohttp.ClientSession) -> BytesIO:
    async with session.get(url, headers={'Referer': 'https://app-api.pixiv.net/'}) as response:
      data = await response.read()
      data = BytesIO(data)
      data.name = url.rpartition('/')[2]
      return data

  def _get_author_icon(self, details:JsonDict) -> str:
    try:
      urls:dict = details.illust.user.profile_image_urls
      return next(iter(urls.values()))
    except KeyError as e:
      return None
  
  def _safe_for_work(self, details:JsonDict) -> bool:
    return details.illust.x_restrict == 0
  
  async def _process_ugoira_video(self, id:int, api:AppPixivAPI) -> str:
    success = await get_ugoira_frames(id, f"./cache/ugoira_{id}/", api)
    if not success:
      logger.warning(f"Was unable to retrieve ugoira data for pixiv post {id}")
      return None
    convert_ugoira_frames(
            f"./cache/ugoira_{id}/",
            f"output.webm",
            "ffmpeg",
            "-c:v libvpx -crf 10 -b:v 2M -an -loglevel error"
        )
    return os.path.abspath(f"./cache/ugoira_{id}/output.webm")
