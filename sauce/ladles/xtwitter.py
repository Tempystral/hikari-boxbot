import html
import json
from logging import getLogger
from re import Match

import aiohttp
from dacite import from_dict
from decouple import config
from hikari import Color
from sauce.response import FXTwitterResponse, SauceResponse, Tweet

from . import Ladle

logger = getLogger("ladles.xtwitter")

class XTwitter(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?:mobile\.)?(?P<domain>twitter|x)\.com/(?P<user>[a-zA-Z0-9_]+)/status/(?P<id>\d+)'

  async def extract(self, match: Match, session: aiohttp.ClientSession) -> SauceResponse:
    tweet_id = match.group("id")
    user = match.group("user")

    response = await self._get_tweet(session, user, tweet_id)
    if not response.code == 200:
      return
    
    tweet = response.tweet

    photos, videos = self._get_tweet_media(tweet)

    response = SauceResponse(
      title = self._build_title(tweet),
      description = self._build_description(tweet),
      url = tweet.url,
      author_name = f"{tweet.author.name} (@{tweet.author.screen_name})",
      author_url = tweet.author.url,
      author_icon = tweet.author.avatar_url,
      images = photos,
      text = f"https://fxtwitter.com/{user}/status/{tweet_id}/" if videos else None,
      video = videos[0] if videos[0] else None,
      color = Color(0x1d9bf0)
    )

    return response

  def _build_title(self, tweet: Tweet):
    return f"{tweet.replies} 💬\t{tweet.retweets} 🔁\t{tweet.likes} 💗\t{tweet.views} 👀"

  def _build_description(self, tweet: Tweet):
    description = tweet.text
    if (quote := tweet.quote):
      description += f"\n\n ⤵ Quoting [{quote.author.name}]({quote.author.url}):"
      description += f"\n{quote.text}"
    return description

  def _get_tweet_media(self, tweet: Tweet):
    photos = []
    videos = []
    if tweet.media:
      if tweet.media.photos:
        photos = [p.url for p in (tweet.media.photos or [])]
      if tweet.media.videos:
        videos = [v.url for v in (tweet.media.videos or [])]
    return photos, videos

  async def _get_tweet(self, session: aiohttp.ClientSession, user: str, id: str) -> FXTwitterResponse:
    response = await session.get(f"https://api.fxtwitter.com/{user}/status/{id}/")
    data = json.loads(await response.text())
    return from_dict(data_class=FXTwitterResponse, data=data)

  async def cleanup(self, match:Match) -> None:
    pass