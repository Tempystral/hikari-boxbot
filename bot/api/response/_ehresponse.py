from dataclasses import dataclass, field
from enum import Enum
from typing import List, TypeAlias

EH_ID: TypeAlias = str | int | None

class Category(Enum):
  DOUJINSHI = "Doujinshi"
  MANGA = "Manga"
  ARTIST_CG = "Artist CG"
  GAME_CG = "Game CG"
  WESTERN = "Western"
  IMAGESET = "Image Set"
  NON_H = "Non-H"
  COSPLAY = "Cosplay"
  ASIAN_PORN = "Asian Porn"
  MISC = "Misc"
  PRIVATE = "Private"

@dataclass
class EHResponse:
  gid: int
  token: str
  archiver_key: str
  title: str
  title_jpn: str
  category: Category
  thumb: str
  uploader: str
  posted: int
  filecount: str | int
  filesize: str | int
  expunged: bool
  rating: str | int
  torrentcount: str | int
  torrents: List["Torrent"] = field(default_factory=list)
  tags: List[str] = field(default_factory=list)
  parent_gid: EH_ID = None
  parent_key : EH_ID = None
  current_gid: EH_ID = None
  current_key: EH_ID = None
  first_gid: EH_ID = None
  first_key: EH_ID = None

@dataclass
class Torrent:
  hash: str
  added: str
  name: str
  tsize: str
  fsize: str