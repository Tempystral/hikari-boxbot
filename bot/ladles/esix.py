import logging
from re import Match

from aiohttp import ClientSession
from hikari import Color

from bot.api import ESixApi, EsixApiException
from bot.api.response import SauceResponse, eSixPoolResponse
from bot.ladles import Ladle

logger = logging.getLogger("ladles.esix")

_api = ESixApi()

class ESixPool(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    pool_id = match.group("id")
    _api.session = session

    try:
      pool = await _api.get_pool(pool_id)
      posts = await self.__get_pool_images(pool)
      posts = sorted(posts, key=lambda p: pool.post_ids.index(p.id))
    except EsixApiException as e:
      logger.warning(f"Could not retrieve e621 pool data due to error {e.code}: {e.reason} -> {e.data}")
      raise e

    response = SauceResponse(
      title = f"Pool{': ' + pool.name.replace('_', ' ') if pool.name else None}",
      description = pool.description,
      url = match[0],
      images = [ post.file.url for post in posts ],
      color = Color(0x246cab),
      count = pool.post_count,
      timestamp=pool.created_at
    )
    return response
  
  def __get_pool_images(self, pool: eSixPoolResponse, limit:int = 4):
    return _api.get_posts(pool.post_ids[:limit])
    
  async def cleanup(self, match:Match) -> None:
      pass
