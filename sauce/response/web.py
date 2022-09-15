import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union
from urllib.parse import urlencode

import bbcode
from dateutil import parser as dp
from utils.mlstripper import strip_tags


class WebResponse():
  def parseTimestamp(self, isoString:str) -> datetime:
    try:
      timestamp = datetime.fromisoformat(isoString)
    except ValueError as e:
      timestamp = datetime(1,1,1,0,0)
    return timestamp

class eSixResponse(WebResponse):
  def parseBBCode(self, text: str) -> str:
    parser = bbcode.Parser()
    parser.install_default_formatters()
    parser.add_simple_formatter("spoiler", "||%(value)s||")
    parser.replace_cosmetic = True
    parsed_text = parser.format(text)

    tag = re.compile("(\[\[(.*?)?\]\])")
    for match in tag.findall(parsed_text):
      parsed_text = parsed_text.replace(match[0], f'[{match[1]}](https://e621.net/wiki_pages/show_or_new?{urlencode({"title": match[1]})})')
    
    return parsed_text

@dataclass()
class eSixPoolResponse(eSixResponse):
  id: int
  name: str
  created_at: Union[str, datetime]
  updated_at: Union[str, datetime]
  creator_id: int
  description: str
  is_active: bool
  category: str
  is_deleted: bool
  creator_name: str
  post_count: int
  post_ids: list[int] = field(default_factory=list)

  def __post_init__(self):
    self.description = strip_tags(self.parseBBCode(self.description))
    self.created_at = self.parseTimestamp(self.created_at)
    self.updated_at = self.parseTimestamp(self.updated_at)