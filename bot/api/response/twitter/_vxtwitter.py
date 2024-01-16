import datetime
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, Optional

from bot.api.response.twitter._sharedtwitter import Tweet, TweetAuthor


@dataclass(slots=True)
class VXTwitterResponse(Tweet):
  date: str
  date_epoch: int
  likes: int
  replies: int
  retweets: int
  text: str
  tweetID: str
  tweetURL: str
  user_name: str
  user_screen_name: str
  possibly_sensitive: bool | None
  qrtURL: str | None
  hashtags: list[str] = field(default_factory=list)
  mediaURLs: list[str] = field(default_factory=list)
  media_extended: list["VXMedia"] = field(default_factory=list)

  @property
  def title(self):
    return f"{self.replies} 💬\t{self.retweets} 🔁\t{self.likes} 💗"

  @property
  def description(self):
    description = self.text
    if self.qrtURL:
      description += f"\n\n ⤵ Quoting {self.qrtURL}"
    return description
  
  @property
  def media(self):
    photos = [m.url for m in self.media_extended if m.type == "image"]
    videos = [m.url for m in self.media_extended if m.type == "video" and m.duration_millis < 600000]
    return photos, videos

  @property
  def author(self):
    return TweetAuthor(
      avatar_url = None,
      display_name = self.user_name,
      username = self.user_screen_name
    )

  @property
  def created_at(self):
    return datetime.fromtimestamp(self.date_epoch, tz=UTC)
  
  @property
  def service(self):
    return "VXTwitter"


@dataclass(slots=True)
class VXMedia:
  altText: Optional[str]
  size: "VXDimensions"
  duration_millis: float
  thumbnail_url: str
  type: Literal["video", "image"]
  url: str

@dataclass(slots=True)
class VXDimensions:
  height: int
  width: int