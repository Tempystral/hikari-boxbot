from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

@dataclass
class FXTwitterResponse:
  code: int
  message: str
  tweet: "Tweet"

@dataclass
class Tweet:
  id: str
  url: str
  text: str
  author: "Author"
  created_at: str
  created_timestamp: int
  replies: int
  retweets: int
  likes: int
  views: int | None
  possibly_sensitive: bool | None
  is_note_tweet: bool
  lang: str
  source: str
  replying_to: str | None
  replying_to_status: str | None
  color: str | None
  twitter_card: Literal['tweet', 'summary', 'summary_image_large', 'player']
  media: Optional["Media"]
  quote: Optional["Quote"]
  poll: Optional["Poll"]
  translation: Optional["TweetTranslation"]

@dataclass
class Author:
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
  website: Optional["Website"]

@dataclass
class Website:
  url: str
  display_url: str

@dataclass
class Quote:
  url: str
  id: str
  text: str
  author: Author
  replies: int
  retweets: int
  likes: int
  color: str | None
  twitter_card: str
  created_at: str
  created_timestamp: int
  possibly_sensitive: bool | None
  views: int
  is_note_tweet: bool
  lang: str
  replying_to: str | None
  replying_to_status: str | None
  media: "Media"
  source: str

@dataclass
class Poll:
  choices: List[Dict]
  total_votes: int
  ends_at: str
  time_left_en: str

@dataclass
class AllMediaEntity:
  type: str
  url: str
  width: int
  height: int
  duration: float | None = None
  altText: str | None = None
  format: str | None = None
  thumbnail_url: str | None = None

@dataclass
class Photo:
  type: str
  url: str
  width: int
  height: int
  altText: str

@dataclass
class Video:
  type: str
  url: str
  width: int
  height: int
  thumbnail_url: str
  duration: float
  format: str

@dataclass
class MosaicFormats:
  ''' Provides urls for both jpeg and
  webp formats for the fxtwitter media mosaic.'''
  jpeg: str
  webp: str

@dataclass
class Mosaic:
  '''Provides the data for a media mosaic'''
  type: str
  formats: MosaicFormats

@dataclass
class Media:
  '''Provides data for a media object'''
  mosaic: Mosaic | None
  all: list[AllMediaEntity] | None = field(default_factory=list)
  external: list[AllMediaEntity] | None = field(default_factory=list)
  photos: list[Photo] | None = field(default_factory=list)
  videos: list[Video] | None = field(default_factory=list)

@dataclass
class TweetTranslation:
  text: str
  source_lang: str
  target_lang: str





