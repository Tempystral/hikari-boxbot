from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FXTwitterResponse:
  code: int
  message: str
  tweet: "Tweet"

@dataclass
class Tweet:
  url: str
  id: str
  text: str
  author: "Author"
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
  media: Optional["Media"]
  source: str
  quote: Optional["Quote"]

@dataclass
class Author:
  id: str
  name: str
  screen_name: str
  avatar_url: str
  avatar_color: str | None
  banner_url: str
  description: str
  location: str
  url: str
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
class AllMediaEntity:
  type: str
  url: str
  width: int
  height: int
  altText: str | None
  thumbnail_url: str | None
  duration: float | None
  format: str | None

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
  photos: list[Photo] | None = field(default_factory=list)
  videos: list[Video] | None = field(default_factory=list)







