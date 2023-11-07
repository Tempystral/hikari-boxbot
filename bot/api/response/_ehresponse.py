from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import List, TypeAlias, TypedDict

EH_ID: TypeAlias = str | int | None

class EHCategory(Enum):
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

@dataclass(slots=True)
class EHGalleryResponse:
  gmetadata: List["EHGallery"] = field(default_factory=list)

@dataclass(slots=True)
class EHGallery:
  gid: int
  token: str
  archiver_key: str
  title: str
  title_jpn: str
  category: EHCategory
  thumb: str
  uploader: str
  posted: str
  filecount: str
  filesize: int
  expunged: bool
  rating: str
  torrentcount: str
  torrents: List["Torrent"] = field(default_factory=list)
  tags: List[str] = field(default_factory=list)
  parent_key : str | None = None
  current_key: str | None = None
  first_key: str | None = None
  parent_gid: str | None = None
  current_gid: str | None = None
  first_gid: str | None = None

@dataclass(slots=True)
class Torrent:
  hash: str
  added: str
  name: str
  tsize: str
  fsize: str

class TokenList(TypedDict):
  gid: int
  token: str