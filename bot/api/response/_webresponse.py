from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Literal, TypedDict
from urllib.parse import urlencode

import bbcode

from bot.utils.mlstripper import strip_tags


class WebResponse():
  def parseTimestamp(self, isoString:str) -> datetime:
    try:
      timestamp = datetime.fromisoformat(isoString)
    except ValueError as e:
      timestamp = datetime(1,1,1,0,0)
    return timestamp

class eSixResponse(WebResponse):
  def _parseBBCode(self, text: str) -> str:
    parser = bbcode.Parser()
    parser.install_default_formatters()
    parser.add_simple_formatter("spoiler", "||%(value)s||")
    parser.replace_cosmetic = True
    parsed_text = parser.format(text)

    tag = re.compile(r'(\[\[(.*?)?\]\])')
    for match in tag.findall(parsed_text):
      parsed_text = parsed_text.replace(match[0], f'[{match[1]}](https://e621.net/wiki_pages/show_or_new?{urlencode({"title": match[1]})})')
    
    return parsed_text

@dataclass(slots=True)
class eSixPoolResponse(eSixResponse):
  id: int
  name: str
  created_at: datetime | str
  updated_at: datetime | str
  creator_id: int
  is_active: bool 
  category: Literal["series", "collection"]
  post_count: int
  description: str = ""
  creator_name: str | None = ""
  post_ids: List[int] = field(default_factory=list)

  def __post_init__(self):
    self.description = strip_tags(self._parseBBCode(self.description))
    self.created_at = self.parseTimestamp(self.created_at)
    self.updated_at = self.parseTimestamp(self.updated_at)

@dataclass(slots=True)
class eSixPostResponse(eSixResponse):
  # TODO Replace these dict unions with just the type whenever dacite supports TypedDict directly
  id: int
  created_at: datetime | str
  updated_at: datetime | str
  change_seq: int
  flags: 'ESixFlags' | Dict
  rating: Literal['s', 'q', 'e']
  fav_count: int
  relationships: 'ESixRelationship' | Dict
  approver_id: int | None
  uploader_id: int
  description: str | None
  comment_count: int
  is_favorited: bool
  has_notes: bool
  duration: float | None
  file: 'ESixFile'
  preview: 'ESixPreview' | Dict
  sample: 'ESixSample' | Dict
  score: 'ESixScore' | Dict
  tags: Dict[str, List[str]] = field(default_factory=dict)
  locked_tags: List[str] = field(default_factory=list)
  sources: List[str] = field(default_factory=list)
  pools: List[int] = field(default_factory=list)

  def __post_init__(self):
    self.description = strip_tags(self._parseBBCode(self.description))
    self.created_at = self.parseTimestamp(self.created_at)
    self.updated_at = self.parseTimestamp(self.updated_at)

@dataclass(slots=True)
class ESixFile():
  width: int
  height: int
  ext: str
  size: int
  md5: str
  url: str

class ESixSample(TypedDict):
  has: bool
  width: int | None
  height: int | None
  url: str | None
  alternates: Dict | None

class ESixPreview(TypedDict):
  width: int
  height: int
  url: str

class ESixScore(TypedDict):
  up: int
  down: int
  total: int

class ESixFlags(TypedDict):
  pending: bool
  flagged: bool
  note_locked: bool
  status_locked: bool
  rating_locked: bool
  deleted: bool

class ESixRelationship(TypedDict):
  parent_id: int | None
  has_children: bool
  has_active_children: bool
  children: List[int]