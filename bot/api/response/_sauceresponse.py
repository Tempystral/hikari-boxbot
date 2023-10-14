from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone, tzinfo
import logging
from typing import Any, Optional
from hikari.files import Resourceish

from hikari.embeds import Embed

logger = logging.getLogger("bot.api.response.SauceResponse")

@dataclass
class SauceResponse():
  '''
  A response object containing all the contents required for an embed.

  Parameters
  ----------
  `title` : The title of the post.
  `description` : The description of the post, if it exists.
  `url` : A link to the post.
  `image` : A Resourceish type. Can be a url to an image or a file, or any other resource accepted by Hikari. If not set, defaults to the first item in `images`
  `images` : A list of Resourceish objects. Use this for albums and collections linked together from one post.
  `author_name` : The display name of whoever posted the image(s).
  `author_url` : A link to the author's profile.
  `author_icon` : The author's profile image.
  `color` : Optional color for the embed. British spelling is ignored if both are set.
  `count` : Optional post count. This value will be derived from the length of `images` if it is set, overriding this value.
  `video` : Optional Resourceish parameter for video content. Use this for webm, mp4, etc.
  `text` : Optional String parameter. If this is set, no embed will be generated, and text will be returned as-is.
  `timestamp`: Optional parameter. May be any one of a datetime, int, float, or ISO-format date string.
  '''
  title : str | None = None
  description : str | None = None
  url : str | None = None
  image : Resourceish | None = None
  images : list[Resourceish] | None = field(default_factory=list)
  author_name : str | None = None
  author_url : str | None = None
  author_icon : str | None = None
  color : str | None = None
  count : int | None = None
  video : Resourceish | None = None
  text : str | None = None
  timestamp: datetime | int | float | str | None = None

  def __post_init__(self):
    if not self.images:
      self.images = []
    self.image = (self.image if self.image else (self.images[0] if self.images else None))
    self.count = self.count or (len(self.images) if self.images else None) or "Unknown"
    self.timestamp = self.__init_timestamp(self.timestamp)

  def to_embeds(self) -> Optional[list[Embed]]:
    '''
    Creates a discord embed from the response object containing all the response details. Also contains the first image in `images`, if any.
    '''
    if self.text:
      return None
    embed = (
      Embed(title = self.title, description=self.description, url=self.url, color=self.color, timestamp=self.timestamp)
      .set_author(name=self.author_name, url=self.author_url, icon=self.author_icon)
      .set_image(self.image)
    )
    if self.count:
      embed.add_field(name="Image Count", value=self.count)
      
    # Test at generating extra embeds from multiple images?
    extra_embeds = [Embed(url=self.url).set_image(image) for image in self.images[1:]]
    return [embed, *extra_embeds]
  
  def get_images(self, limit:int = 3) -> list[Resourceish]:
    '''
    Returns a list of images from this response object, from the second element in `images` to the last, or up to some limit (inclusive).
    '''
    if not self.images:
      return []
    if len(self.images) >= limit + 1:
      return self.images[1:limit+1]
    else:
      return self.images[1:]
  
  def __init_timestamp(self, ts: int | float | str | datetime):
    if isinstance(ts, int | float):
      return datetime.fromtimestamp(ts, tz=UTC)
    elif isinstance(ts, str):
      try:
        return datetime.fromisoformat(ts)
      except TypeError as e:
        logger.error("Attempted to marshal a non-ISO string into a datetime!")
        return None
    return ts

  def __str__(self) -> str:
    return str(self.__dict__)