import asyncio
from typing import Sequence

import hikari
import hikari.errors
import lightbulb


async def get_emoji(bot: lightbulb.BotApp, guilds: Sequence[hikari.Snowflakeish]):
  coros = [ get_emoji(bot, guild) for guild in guilds ]
  emojilists:Sequence[hikari.Emoji] = await asyncio.gather(*[c for c in coros if c != None])
  return dict(zip(guilds, emojilists))

def get_emoji(bot: lightbulb.BotApp, guild: hikari.Snowflakeish):
  try:
    return bot.rest.fetch_guild_emojis(guild)
  except hikari.errors.NotFoundError as e:
    return None