from asyncio import TaskGroup
import logging
import random
from re import Match, Pattern

import hikari
import lightbulb as lb
from decouple import config

from bot.ladles import Ladle
from bot.utils import bot_utils, sauce_utils
from bot.utils.config.errors import GuildNotFoundError
from bot.utils.config.serverConfig import ServerConfig

logger = logging.getLogger("BoxBot.modules.sauce")

sauce_plugin = lb.Plugin("Sauce")

@sauce_plugin.listener(hikari.GuildMessageCreateEvent)
async def sauce(event: hikari.GuildMessageCreateEvent):
  if _do_not_sauce(event):
    return
  
  # Get a list of links from the message
  msg = sauce_utils.remove_spoilered_text(event.content)
  reply:hikari.Message
  logger.debug(f"Message: {msg}")
  links = _find_links(msg, event.guild_id)

  if links:
    reply = await event.message.respond("Saucing media, one moment...",
                                        reply=event.message.id,
                                        flags = hikari.MessageFlag.LOADING | hikari.MessageFlag.SUPPRESS_NOTIFICATIONS)

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata
  for ladle, matched_link in links:
    response = await ladle.extract(match=matched_link, session=sauce_plugin.bot.d.aio_session)
    if not response:
      await reply.delete()
      return
    logger.debug(f"Extracted Data: {response.__repr__()}")
    
    # Once metadata is retrieved, send it off to the embed generator
    embeds = response.to_embeds() if response else []
    if embeds:
      await _add_random_footer_icon(event.guild_id, embeds[0])

    # Post the embed + suppress embeds on original message
    if embeds or response.text:
      async with TaskGroup() as tg:
        suppressTask = tg.create_task(event.message.edit(flags=hikari.MessageFlag.SUPPRESS_EMBEDS))
        deleteLoadingTask = tg.create_task(reply.delete())
        finalReplyTask = tg.create_task(event.message.respond(
                                       reply=event.message.id,
                                       attachment=response.video or hikari.UNDEFINED, # Undefined is NOT None!
                                       embeds=embeds,
                                       content=response.text,
                                       mentions_reply=False))
    # Finally, if necessary...
    await ladle.cleanup(matched_link)
    guild_name = guild.name if (guild := event.get_guild()) else event.guild_id
    logger.info(f"{guild_name} | Msg {event.message_id} | {event.member.username}: {matched_link.string}")

def _find_links(message:str, guild_id: int) -> list[tuple[Ladle, Match]]:
  links = []
  ladle: Ladle
  pattern: Pattern
  for (ladle, pattern) in _get_extractors(sauce_plugin.bot):
    if _extractor_enabled(ladle, guild_id):
      # Find all the matches for a given extractor's pattern in the message
      matches = pattern.finditer(message)
      #logger.debug(f"Matches for pattern: {pattern}: {matches}")
      if matches:
        links.extend([(ladle, match) for match in matches])
  
  if links:
    logger.debug(f"Found the following links: {[m for _, m in links]}")
  return links

async def _add_random_footer_icon(guild: hikari.SnowflakeishOr[hikari.PartialGuild], embed: hikari.Embed):
  if embed.footer:
    if int(guild) in __datastore().emojis:
      emojis = __datastore().emojis[int(guild)]
    else:
      newemojis = await bot_utils.get_emoji(sauce_plugin.bot, [int(guild)])
      __datastore().emojis = __datastore().emojis | newemojis
    emoji = random.choice([e for e in emojis if not e.is_animated])
    embed.set_footer(embed.footer.text, icon=emoji)
  
def _do_not_sauce(event: hikari.GuildMessageCreateEvent):
  if (not event.content) or event.author.is_bot:
    return True
  if __datastore().testmode:
    if not event.channel_id == __datastore().test_channel:
      return True
  try:
    guild = get_settings().get_guild(event.guild_id)
    if event.channel_id in guild.channel_exclusions:
        return True
  except GuildNotFoundError as e:
    return True
  
  return False

def __datastore():
  return sauce_plugin.bot.d

def get_settings() -> ServerConfig:
  return __datastore().settings

def _extractor_enabled(ladle: Ladle, guild_id: int):
  return ladle.__class__.__name__ in get_settings().get_guild(guild_id).extractors

def _get_extractors(bot: lb.BotApp) -> tuple[Ladle, Pattern]:
    return bot.d.extractors

def _set_extractors(bot: lb.BotApp) -> None:
  l_extractors = config("EXTRACTORS", cast=str).split(",")
  l_ladles = sauce_utils.get_ladles(l_extractors)
  bot.d.extractors = sauce_utils.compile_patterns(l_ladles)

def load(bot: lb.BotApp) -> None:
  _set_extractors(bot)
  logger.debug(f"Loaded extractors: {[(l, e.pattern) for l, e in _get_extractors(bot)]}")
  if bot.d.testmode:
    logger.warning("Loaded in test mode!")
  bot.add_plugin(sauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(sauce_plugin)
