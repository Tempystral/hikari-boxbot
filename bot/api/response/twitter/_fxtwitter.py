from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List, Optional

from bot.api.response.twitter._sharedtwitter import Tweet, TweetAuthor


@dataclass(slots=True)
class FXTwitterResponse(Tweet):
  code: int
  message: str
  tweet: Optional["FXTweet"]

  @property
  def title(self):
    if not self.tweet:
      return ""
    return f"{self.tweet.replies} 💬\t{self.tweet.retweets} 🔁\t{self.tweet.likes} 💗\t{self.tweet.views} 👀"

  @property
  def description(self):
    if not self.tweet:
      return ""
    desc = self.tweet.text
    if (quote := self.tweet.quote):
      desc += f"\n\n ⤵ Quoting [{quote.author.name}]({quote.author.url}):"
      desc += f"\n{quote.text}"
    return desc
  
  @property
  def media(self):
    photos = []
    videos = []
    if self.tweet and self.tweet.media:
      if self.tweet.media.photos:
        photos = [p.url for p in (self.tweet.media.photos[:4] or [])]
      if self.tweet.media.videos:
        videos = [v.url for v in (self.tweet.media.videos or []) if v.duration < 600]
    return photos, videos
  
  @property
  def author(self):
    return TweetAuthor(
      avatar_url = self.tweet.author.avatar_url,
      username = self.tweet.author.screen_name,
      display_name = self.tweet.author.name
    )

  @property
  def created_at(self):
    if not self.tweet:
      return datetime.now()
    return datetime.fromtimestamp(self.tweet.created_timestamp, tz=UTC)
  
  @property
  def service(self):
    return "FXTwitter"

@dataclass(slots=True)
class FXTweet:
  id: str
  url: str
  text: str
  author: "FXAuthor"
  created_at: str
  created_timestamp: int
  replies: int
  retweets: int
  likes: int
  views: int | None
  possibly_sensitive: bool | None
  is_note_tweet: bool
  lang: str
  source: str | None
  replying_to: str | None
  replying_to_status: str | None
  color: str | None
  twitter_card: str | None
  media: Optional["FXMedia"]
  quote: Optional["FXTweet"]
  poll: Optional["FXPoll"]
  translation: Optional["FXTweetTranslation"]

@dataclass(slots=True)
class FXAuthor:
  id: str
  name: str
  screen_name: str
  avatar_url: str | None
  avatar_color: str | None
  banner_url: str | None
  description: str | None
  location: str | None
  url: str | None
  followers: int
  following: int
  joined: str
  tweets: int
  likes: int
  website: Optional["FXWebsite"]

@dataclass(slots=True)
class FXWebsite:
  url: str
  display_url: str

@dataclass(slots=True)
class FXPoll:
  choices: List[Dict]
  total_votes: int
  ends_at: str
  time_left_en: str

@dataclass(slots=True)
class FXMediaEntity:
  type: str
  url: str
  width: int
  height: int
  duration: float | None = None
  altText: str | None = None
  format: str | None = None
  thumbnail_url: str | None = None

@dataclass(slots=True)
class FXPhoto:
  type: str
  url: str
  width: int
  height: int
  altText: str

@dataclass(slots=True)
class FXVideo:
  type: str
  url: str
  width: int
  height: int
  thumbnail_url: str
  duration: float
  format: str

@dataclass(slots=True)
class FXMosaicFormats:
  ''' Provides urls for both jpeg and
  webp formats for the fxtwitter media mosaic.'''
  jpeg: str
  webp: str

@dataclass(slots=True)
class Mosaic:
  '''Provides the data for a media mosaic'''
  type: str
  formats: FXMosaicFormats

@dataclass(slots=True)
class FXMedia:
  '''Provides data for a media object'''
  mosaic: Mosaic | None
  external: FXMediaEntity | None = None
  all: list[FXMediaEntity] | None = field(default_factory=list)
  photos: list[FXPhoto] | None = field(default_factory=list)
  videos: list[FXVideo] | None = field(default_factory=list)

@dataclass(slots=True)
class FXTweetTranslation:
  text: str
  source_lang: str
  target_lang: str





