from __future__ import annotations

import json
from logging import getLogger
import os
from dataclasses import dataclass, field
from typing import Sequence, Set, TypeVar

from hikari import Role
from hikari.channels import GuildChannel

from dataclass_wizard import JSONWizard
from bot.utils.config.errors import GuildExistsError, GuildNotFoundError

log = getLogger("BoxBot.util.config")

T = TypeVar("T")

settings: ServerConfig | None = None

def _save_settings(settings: ServerConfig, file:str = "./settings.json") -> None:
  options = "w" if os.path.exists(file) else "x"
  with open(file, options) as f:
    f.write(settings.to_json(encoder=json.dumps, indent=2))

def _load_settings(file:str) -> ServerConfig:
  if not os.path.exists(file):
    settings = ServerConfig(guilds={})
    with open(file, "w") as f:
      f.write(settings.to_json())
  else:
    with open(file, "r") as f:
      data = json.load(f)
      settings = ServerConfig.from_dict(data)
  return settings

def get_settings(filename:str = "./settings.json") -> ServerConfig:
  return settings if settings else _load_settings(filename)

@dataclass
class GuildConfig:
  name:str
  guild_id:int
  test_channel:int | None = None
  sauce_in_threads:bool = False
  channel_exclusions:set[int] = field(default_factory=set)
  elevated_roles:set[int] = field(default_factory=set)
  extractors:set[str] = field(default_factory=set)

@dataclass
class ServerConfig(JSONWizard):
  class _(JSONWizard.Meta):
    key_transform_with_load = "SNAKE"
    key_transform_with_dump = "SNAKE"

  guilds: dict[int, GuildConfig] = field(default_factory=dict)

  def save(self, file: str | None = None) -> None:
    _save_settings(self, file) if file else _save_settings(self)

  def add_guild(self, guild_id: int, guild_name: str):
    if guild_id in self.guilds:
      raise GuildExistsError("Guild already exists!")
    self.guilds.setdefault(guild_id, GuildConfig(guild_id=guild_id, name=guild_name))
     
  def set_name(self, guild_id: int, name:str):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].name = name

  def set_sauce_in_threads(self, guild_id: int, allowed:bool):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].sauce_in_threads = allowed

  def set_test_channel(self, guild_id: int, channel: GuildChannel):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].test_channel = channel.id
    return channel.id

  def set_excluded_channels(self, guild_id: int, channels: Sequence[GuildChannel]):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].channel_exclusions = set([c.id for c in channels])
    return channels

  def add_excluded_channel(self, guild_id: int, channel: GuildChannel):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].channel_exclusions.add(channel.id)
    return channel.id
  
  def remove_excluded_channel(self, guild_id: int, channel: GuildChannel):
    self.__guild_exists(guild_id)
    self.__remove(self.guilds[guild_id].channel_exclusions, channel.id)
    return channel.id

  def set_elevated_roles(self, guild_id: int, roles: Sequence[Role]):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].elevated_roles = set([r.id for r in roles])
    return roles

  def add_elevated_role(self, guild_id: int, role: Role):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].elevated_roles.add(role.id)
    return role.id
  
  def remove_elevated_role(self, guild_id: int, role: Role):
    self.__guild_exists(guild_id)
    self.__remove(self.guilds[guild_id].elevated_roles, role.id)
    return role.id
  
  def set_extractors(self, guild_id: int, ladles: Sequence[str]):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].extractors = set(ladles)
    return ladles

  def add_extractor(self, guild_id: int, ladle:str):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].extractors.add(ladle)
    return ladle
  
  def remove_extractor(self, guild_id: int, ladle:str):
    self.__guild_exists(guild_id)
    self.__remove(self.guilds[guild_id].extractors, ladle)
    return ladle

  def get_guild(self, guild_id: int):
    self.__guild_exists(guild_id)
    return self.guilds[guild_id]
  
  def __remove(self, collection:Set[T], item: T):
    if (item in collection):
      collection.remove(item)

  def __guild_exists(self, guild_id):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `/admin setup`")