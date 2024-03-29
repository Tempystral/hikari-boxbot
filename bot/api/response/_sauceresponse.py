from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from hikari.embeds import Embed
from hikari.files import Resourceish

logger = logging.getLogger("bot.api.response.SauceResponse")

@dataclass(slots=True)
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
  author_name : str | None = None
  author_url : str | None = None
  author_icon : str | None = None
  images : list[Resourceish] | None = field(default_factory=list)
  count : int | None = None
  video : Resourceish | None = None
  color : str | None = None
  text : str | None = None
  timestamp: datetime | int | float | str | None = None
  via : str | None = "Boxbot"

  def __post_init__(self):
    if self.count is None:
      self.count = len(self.images) if self.images else 0
    self.timestamp = self.__init_timestamp(self.timestamp)

  def to_embeds(self) -> list[Embed]:
    '''
    Creates an array of discord embeds from the response object. The first embed contains all response details.
    If there are multiple images in the response, up to 3 additional embeds are generated, which Discord will
    merge together in the client.
    '''
    if self.text:
      return []
    embed = (
      Embed(title = self.title, description=self.description, url=self.url, color=self.color, timestamp=self.timestamp)
      .set_author(name=self.author_name, url=self.author_url, icon=self.author_icon)
      .set_image(self.images[0] if self.images else None)
      .set_footer(f"via {self.via}")
    )
    if not self.count == 0:
      embed.add_field(name="Image Count", value=self.count, inline=True)
      
    # Test at generating extra embeds from multiple images?
    extra_embeds = [ Embed(url=self.url).set_image(image) for image in self.images[1:] ]
    return [embed, *extra_embeds]
  
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