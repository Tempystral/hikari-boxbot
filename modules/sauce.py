from re import Match
from typing import Tuple
from decouple import config

import hikari
import lightbulb as lb

from sauce import SauceResponse, util
from sauce.checks import on_bot_message, reply_only, user_replied_to
from sauce.ladles.abc import Ladle

import logging
logger = logging.getLogger("Sauce")

sauce_plugin = lb.Plugin("Sauce")

@sauce_plugin.listener(hikari.GuildMessageCreateEvent)
async def sauce(event: hikari.GuildMessageCreateEvent):
  if (not event.content) or event.author.is_bot:
    return
  
  # Get a list of links from the message
  msg = util.remove_spoilered_text(event.content)
  links = find_links(msg)

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata
  for ladle, matched_link in links:
    response:SauceResponse = await ladle.extract(match=matched_link, session=sauce_plugin.bot.d.aio_session)

    # Once metadata is retrieved, send it off to the embed generator
    embed = response.to_embed()
    # Post the embed + suppress embeds on original message
    if embed:
      await event.message.edit(flags=hikari.MessageFlag.SUPPRESS_EMBEDS)
      await event.message.respond(embed, reply=event.message.id, mentions_reply=False) # Reply, but don't mention. We can reference this value later.

@sauce_plugin.command
@lb.add_checks(on_bot_message, reply_only, user_replied_to | lb.has_roles(role1=sauce_plugin.bot.d.roles))
@lb.command("oops", "Purge the last message BoxBot sauced for you.")
@lb.implements(lb.MessageCommand)
async def oops(ctx: lb.MessageContext) -> None:
  message:hikari.Message = ctx.options.target
  msg = await ctx.bot.rest.fetch_message(message.channel_id, message.id)
  await ctx.respond(f"Ran command {ctx.command.name} on {msg.id}\nMessage type: {msg.type}\nReferenced message: {msg.referenced_message.id}\n")

@sauce_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> None:
  logger.warning(f"Exception triggered: {event.exception}")
  await event.context.respond("\n".join(event.exception.args[0].split(", ")), flags=hikari.MessageFlag.EPHEMERAL)
  return True # To tell the bot not to propogate this error event up the chain

def find_links(message:str) -> list[Tuple[Ladle, Match]]:
  links = []
  for ext, pattern in sauce_plugin.bot.d.extractors:
    # Find all the matches for a given extractor's pattern in the message
    matches = pattern.finditer(message)
    if matches:
      return ([(ext, match) for match in matches])
  return links

def load(bot: lb.BotApp) -> None:

  bot.d.roles = config("ELEVATED_ROLES", cast=str)
  l_extractors = config("EXTRACTORS", cast=str, strip=" ").split(",")
  bot.d.extractors = util.compile_patterns(util.get_ladles(l_extractors))
  bot.add_plugin(sauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(sauce_plugin)
