import asyncio
from typing import Sequence

import hikari
import hikari.errors
import lightbulb


async def get_emoji(bot: lightbulb.BotApp, guilds: Sequence[hikari.Snowflakeish]):
  coros = []
  for guild in guilds:
    c = make_coros(bot, guild)
    if c != None:
      coros.append(c)
  emojilists:Sequence[hikari.Emoji] = await asyncio.gather(*coros)
  return dict(zip(guilds, emojilists))

def make_coros(bot: lightbulb.BotApp, guild: hikari.Snowflakeish):
  try:
    return bot.rest.fetch_guild_emojis(guild)
  except hikari.errors.NotFoundError as e:
    return None