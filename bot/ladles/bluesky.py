import logging
from re import Match

from aiohttp import ClientSession
from atproto import Client
from decouple import config
from hikari import Color

from bot.api.response import SauceResponse
from bot.ladles import Ladle

logger = logging.getLogger("ladles.bsky")

_api = Client().with_bsky_labeler()

class Bluesky(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<domain>bsky\.app)/profile/(?P<user>.+)/post/(?P<id>\w+)'
    login = config("BSKY_USER", cast=str),
    password = config("BSKY_KEY", cast=str)
    _api.login(login[0], password)

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    #site = match.group("domain")
    username = match.group("user")
    post_id = match.group("id")

    author = _api.get_profile(username)
    post = _api.get_post(post_id, username).value
    # logger.debug(post.model_dump_json())
    # logger.debug(author.model_dump_json())

    video = None
    images = []
    count = 0
    if not post.embed:
      return None

    if "media" in post.embed.model_fields_set:
      media = post.embed.media
    else:
      media = post.embed
    
    if "images" in media.model_fields_set:
      images = [self.build_img_url(author.did, img.image.ref.link, img.image.mime_type) for img in media.images]
      count = len(media.images)
    if "video" in media.model_fields_set:
      return SauceResponse(text=f"https://fxbsky.app/profile/{username}/post/{post_id}")
    #  return None # For now it's too much of a pain to get these URLs and stitch together the playlist
    #   #video = self.build_vid_url(author.did, post.embed.video.ref.link, post.embed.video.mime_type)
    
    return SauceResponse(
       author_name=f"{author.display_name} ({author.handle})",
       author_icon=author.avatar,
       author_url=f"https://bsky.app/profile/{author.handle}",
       title="View post on Bluesky",
       url=match.group(),
       description=post.text,
       images=images,
       count = count,
       color=Color(0x1185fe),
       timestamp=post.created_at
    )
  
  def build_img_url(self, did:str, media_link:str, mime_type:str):
     ext = mime_type.split("/")[1]
     return f"https://cdn.bsky.app/img/feed_fullsize/plain/{did}/{media_link}@{ext}"
  
  def build_vid_url(self, did:str, media_link:str):
     # ext = mime_type.split("/")[1]
     return f"https://video.bsky.app/watch/{did}/{media_link}/playlist.m3u8"
    
  async def cleanup(self, match:Match) -> None:
      pass
