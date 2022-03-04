from re import Match
from hikari import Color
from tweepy import Client, User, Media, Tweet, OAuth2BearerHandler, API
import aiohttp
from decouple import config
from sauce import SauceResponse

from . import Ladle

from logging import getLogger

logger = getLogger("ladles.twitter")

class Twitter(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?:mobile\.)?twitter\.com/[a-zA-Z0-9_]+/status/(?P<id>\d+)'
    self.hotlinking_allowed = True

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

    video = None
    images = None
    if media[0].type == "video":
      video = await self.retrieve_video(token, tweet_id)
    elif media[0].type == "photo":
      images = [m.url for m in media]

    response = SauceResponse(
      title = None,
      description = tweet.text,
      url = None,
      author_name = user.username,
      author_url = user.url,
      author_icon = user.profile_image_url,
      images = images,
      video = video,
      colour = Color(0x1d9bf0)
    )

    return response

  async def cleanup(self, match:Match) -> None:
    pass

  async def retrieve_video(self, token:str, tweet_id:str) -> str:
    auth = OAuth2BearerHandler(token)
    api = API(auth)
    data = api.get_status(id=tweet_id, include_entities=True)
    return data._json["extended_entities"]["media"][0]["video_info"]["variants"][0]["url"]