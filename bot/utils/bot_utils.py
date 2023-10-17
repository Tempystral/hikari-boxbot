from asyncio import TaskGroup
import asyncio
from typing import Sequence, TypedDict
import hikari
import lightbulb

async def get_emoji(bot: lightbulb.BotApp, guilds: Sequence[hikari.Snowflakeish]):
  coros = [ bot.rest.fetch_guild_emojis(guild) for guild in guilds ]
  emojilists:Sequence[hikari.Emoji] = await asyncio.gather(*coros)
  return dict(zip(guilds, emojilists))