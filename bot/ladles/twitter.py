import html
from logging import getLogger
from re import Match

import aiohttp
from decouple import config
from hikari import Color
from tweepy import API, Client, Media, OAuth2BearerHandler, Tweet, User

from bot.api.response import SauceResponse
from bot.ladles import Ladle

logger = getLogger("ladles.twitter")

class Twitter(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?:mobile\.)?twitter\.com/[a-zA-Z0-9_]+/status/(?P<id>\d+)'

  async def extract(self, match: Match, session: aiohttp.ClientSession) -> SauceResponse:
    token = config("TWITTER_BEARER")
    client = Client(token)
    tweet_id = match.group("id")

    data = client.get_tweet(id = tweet_id,
                            user_auth = False,
                            expansions = ["attachments.media_keys", "author_id"],
                            media_fields = ["media_key", "alt_text", "url", "type"],
                            tweet_fields = ["attachments", "author_id", "text"],
                            user_fields = ["url", "username", "profile_image_url"]
                            )
    tweet:Tweet = data.data
    user:User = data.includes["users"][0]
    
    try:
      media:list[Media] = data.includes["media"]
    except KeyError as e: # Don't sauce tweets without media
      logger.debug("No media to sauce.")
      return

    text = None
    images = None
    if media[0].type == "video" or media[0].type == "animated_gif":
      text = match.string.replace("twitter", "vxtwitter")
    elif media[0].type == "photo":
      images = [m.url for m in media]

    response = SauceResponse(
      title = None,
      description = html.unescape(tweet.text),
      url = None,
      author_name = user.username,
      author_url = user.url,
      author_icon = user.profile_image_url,
      images = images,
      text = text,
      color = Color(0x1d9bf0)
    )

    return response

  async def cleanup(self, match:Match) -> None:
    pass

  async def retrieve_video(self, token:str, tweet_id:str) -> str:
    auth = OAuth2BearerHandler(token)
    api = API(auth)
    data = api.get_status(id=tweet_id, include_entities=True)
    return data._json["extended_entities"]["media"][0]["video_info"]["variants"][0]["url"]