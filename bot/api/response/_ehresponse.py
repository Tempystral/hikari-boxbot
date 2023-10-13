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

@dataclass
class EHGalleryResponse:
  gmetadata: List["EHGallery"] = field(default_factory=list)

@dataclass
class EHGallery:
  gid: int
  token: str
  archiver_key: str
  title: str
  title_jpn: str
  category: EHCategory
  thumb: str
  uploader: str
  posted: InitVar[str]
  filecount: InitVar[str]
  filesize: int
  expunged: bool
  rating: InitVar[str]
  torrentcount: InitVar[str]
  torrents: List["Torrent"] = field(default_factory=list)
  tags: List[str] = field(default_factory=list)
  parent_key : str | None = None
  current_key: str | None = None
  first_key: str | None = None
  parent_gid: InitVar[str | None] = None
  current_gid: InitVar[str | None] = None
  first_gid: InitVar[str | None] = None

  def __post_init__(self, posted, filecount, rating, torrentcount, parent_gid, current_gid, first_gid):
    self.added_on = int(posted)
    self.file_count = int(filecount)
    self.rating_value = float(rating)
    self.torrent_count = int(torrentcount)
    if parent_gid:
      self.parent_gid_value = int(parent_gid)
    if current_gid:
      self.current_gid_value = int(current_gid)
    if first_gid:
      self.first_gid_value = int(first_gid)

@dataclass
class Torrent:
  hash: str
  added: str
  name: str
  tsize: str
  fsize: str

class TokenList(TypedDict):
  gid: int
  token: str