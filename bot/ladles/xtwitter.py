from logging import getLogger
from re import Match

import aiohttp
from hikari import Color

from bot.api.response import SauceResponse
from bot.api.twitter import TwitterAPI
from bot.ladles import Ladle

logger = getLogger("ladles.xtwitter")

class XTwitter(Ladle):
  def __init__(self):
    self._api: TwitterAPI | None = None
    self.pattern = r'https?://(?:mobile\.)?(?P<domain>twitter|x)\.com/(?P<user>[a-zA-Z0-9_]+)/status/(?P<id>\d+)'

  async def extract(self, match: Match, session: aiohttp.ClientSession) -> SauceResponse:
    if not self._api:
      self._api = TwitterAPI(session)
    
    tweet_id = match.group("id")
    user = match.group("user")

    tweet = await self._api.get_tweet(user, tweet_id)
    if not tweet:
      return None

    photos, videos = tweet.media

    response = SauceResponse(
      title = tweet.title,
      description = tweet.description,
      url = match.group(),
      author_name = f"{tweet.author.display_name} (@{tweet.author.username})",
      author_url = tweet.author.url,
      author_icon = tweet.author.avatar_url,
      images = photos,
      text = None,
      video = videos[0] if videos else None,
      color = Color(0x1d9bf0),
      timestamp = tweet.created_at,
      via = tweet.service
    )

    return response


  async def cleanup(self, match:Match) -> None:
    pass