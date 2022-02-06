import logging
from re import Match
from typing import Tuple

import hikari

import lightbulb as lb
from decouple import config
from sauce import SauceResponse, util
from sauce.checks import on_bot_message, reply_only, user_replied_to
from sauce.checks import CheckFailureWithData
from sauce.ladles.abc import Ladle

logger = logging.getLogger("BoxBot.modules.sauce")

sauce_plugin = lb.Plugin("Sauce")

@sauce_plugin.listener(hikari.GuildMessageCreateEvent)
async def sauce(event: hikari.GuildMessageCreateEvent):
  if (not event.content) or event.author.is_bot:
    return
  
  # Get a list of links from the message
  msg = util.remove_spoilered_text(event.content)
  logger.debug(f"Message: {msg}")
  links = find_links(msg)
  if links: logger.debug(f"Found the following links: {[m for _, m in links]}")

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata
  for ladle, matched_link in links:
    response:SauceResponse = await ladle.extract(match=matched_link, session=sauce_plugin.bot.d.aio_session)
    logger.debug(f"Extracted Data: {response}")
    # Once metadata is retrieved, send it off to the embed generator
    embed = response.to_embed()
    images = response.get_images()
    # Post the embed + suppress embeds on original message
    if embed:
      await event.message.edit(flags=hikari.MessageFlag.SUPPRESS_EMBEDS)
      await event.message.respond(embed, reply=event.message.id, mentions_reply=False) # Reply, but don't mention. We can reference this value later.
    if images: # I would use attachments here, but the 8MB limit applies
      await event.message.respond("\n".join(images), reply=event.message.id, mentions_reply=False)

@sauce_plugin.command
@lb.add_checks(on_bot_message, reply_only, user_replied_to | lb.has_roles(role1=config("ELEVATED_ROLES", cast=str)))
@lb.command("Un-Sauce", "Purge the last message BoxBot sauced for you.")
@lb.implements(lb.MessageCommand)
async def oops(ctx: lb.MessageContext) -> None:
  msg:hikari.Message = ctx.bot.d.pop(ctx.interaction.target_id)

  if msg.embeds[0].title: # msg.embeds both exists and has content in it even when there are no embeds, awesome
    logger.info(f"User {ctx.member.username}#{ctx.member.discriminator} unsauced post {msg.id}.\n\tContent: \"{msg.embeds[0].title}\" by {msg.embeds[0].author.name} - {msg.embeds[0].url}")
  else:
    logger.info(f"User {ctx.member.username}#{ctx.member.discriminator} unsauced post {msg.id}.\n\tContent: \"{msg.content}\"")

  await ctx.respond(f"Ran command {ctx.command.name} on {msg.id}\nMessage type: {msg.type}\nReferenced message: {msg.referenced_message.id}\n")

@sauce_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> None:
  logger.warning(f"Caught exception: {type(event.exception)}")

  if isinstance(event.exception, CheckFailureWithData):
    msg:hikari.Message = event.exception.data
    try:
      # Remove the stored message from the datastore so it doesn't grow
      event.bot.d.pop(msg.id)
      logger.debug(f"Cleaned message {msg.id} from the datastore")
    except (AttributeError, KeyError) as e:
      logger.debug(f"Message {msg.id} not found in datastore.")
    await event.context.respond("\n".join(event.exception.args[0].split(", ")), flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain
  

def find_links(message:str) -> list[Tuple[Ladle, Match]]:
  links = []
  for ext, pattern in sauce_plugin.bot.d.extractors:
    # Find all the matches for a given extractor's pattern in the message
    matches = pattern.finditer(message)
    logger.debug(f"Matches for pattern: {pattern}: {matches}")
    if matches:
      links.extend([(ext, match) for match in matches])
  return links

def load(bot: lb.BotApp) -> None:
  l_extractors = config("EXTRACTORS", cast=str).split(",")
  bot.d.extractors = util.compile_patterns(util.get_ladles(l_extractors))
  logger.debug(f"Loaded extractors: {[(l, e.pattern) for l, e in bot.d.extractors]}")
  bot.add_plugin(sauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(sauce_plugin)
