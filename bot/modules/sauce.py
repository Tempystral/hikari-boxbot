from asyncio import TaskGroup
import logging
import random
from re import Match, Pattern

import hikari
import lightbulb as lb
from decouple import config

from bot.ladles import Ladle
from bot.utils import sauce_utils

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
  links = _find_links(msg)

  if links:
    reply = await event.message.respond("Saucing media, one moment...",
                                        reply=event.message.id,
                                        flags = hikari.MessageFlag.LOADING | hikari.MessageFlag.SUPPRESS_NOTIFICATIONS)

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata
  for ladle, matched_link in links:
    response = await ladle.extract(match=matched_link, session=sauce_plugin.bot.d.aio_session)
    if not response:
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
                                       attachment=response.video or hikari.UNDEFINED, # Undefined is NOT None!
                                       embeds=embeds,
                                       content=response.text,
                                       mentions_reply=False))
    # Finally, if necessary...
    await ladle.cleanup(matched_link)
    logger.info(f"Sauced post {event.message_id} by user {event.member.username}#{event.member.discriminator}: {matched_link.string}")

def _find_links(message:str) -> list[tuple[Ladle, Match]]:
  links = []
  ladle: Ladle
  pattern: Pattern
  for (ladle, pattern) in _get_extractors(sauce_plugin.bot):
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
    emojis = __datastore().emojis[int(guild)]
    emoji = random.choice([e for e in emojis if not e.is_animated])
    embed.set_footer(embed.footer.text, icon=emoji)
  
def _do_not_sauce(event: hikari.Event):
  if (not event.content) or event.author.is_bot:
    return True
  if __datastore().testmode:
    if not event.channel_id == __datastore().test_channel:
      return True
  return False

def __datastore():
  return sauce_plugin.bot.d

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
