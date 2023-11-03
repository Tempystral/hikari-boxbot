from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class Tweet(Protocol):
  
  @property
  def title(self) -> str:
    ...

  @property
  def description(self) -> str:
    ...

  @property
  def media(self) -> tuple[list[str], list[str]]:
    ...

  @property
  def author(self) -> "TweetAuthor":
    ...

  @property
  def created_at(self) -> datetime:
    ...
  
  @property
  def service(self) -> str:
    ...

@dataclass
class TweetAuthor:
  username: str
  display_name: str
  avatar_url: str | None

  @property
  def url(self):
    return f"https://twitter.com/{self.username}"
  