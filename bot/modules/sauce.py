import logging
from re import Match, Pattern

import hikari
import lightbulb as lb
from decouple import config

from bot.utils import sauce_utils
from bot.api.response import SauceResponse
from bot.utils.checks import on_bot_message, reply_only, user_replied_to
from bot.ladles import Ladle

logger = logging.getLogger("BoxBot.modules.sauce")

sauce_plugin = lb.Plugin("Sauce")

@sauce_plugin.listener(hikari.GuildMessageCreateEvent)
async def sauce(event: hikari.GuildMessageCreateEvent):
  if (not event.content) or event.author.is_bot:
    return
  
  if sauce_plugin.bot.d.testmode:
    if event.channel_id == config("TEST_CHANNEL", cast=int):
      pass
    else:
      return
  
  # Get a list of links from the message
  msg = sauce_utils.remove_spoilered_text(event.content)
  #logger.debug(f"Message: {msg}")
  links = _find_links(msg)
  if links: logger.debug(f"Found the following links: {[m for _, m in links]}")

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata
  for ladle, matched_link in links:
    response:SauceResponse = await ladle.extract(match=matched_link, session=sauce_plugin.bot.d.aio_session)
    logger.debug(f"Extracted Data: {response}")
    
    # Once metadata is retrieved, send it off to the embed generator
    embeds  = response.to_embeds()   if response else None
    # images = response.get_images() if response else None

    # Post the embed + suppress embeds on original message
    if embeds or response.text:
      await event.message.edit(flags=hikari.MessageFlag.SUPPRESS_EMBEDS)
      await event.message.respond(attachment=response.video or hikari.UNDEFINED, # Undefined is NOT None!
                                  embeds=embeds,
                                  content=response.text,
                                  reply=event.message.id,
                                  mentions_reply=False)
    # Finally, if necessary...
    await ladle.cleanup(matched_link)
    logger.info(f"Sauced post {event.message_id} by user {event.member.username}#{event.member.discriminator}: {matched_link.string}")

@sauce_plugin.command
@lb.add_checks(on_bot_message, reply_only)
@lb.add_checks(user_replied_to | lb.has_roles(role1=config("ELEVATED_ROLES", cast=int)))
@lb.command("Un-Sauce", "Purge the last message BoxBot sauced for you.")
@lb.implements(lb.MessageCommand)
async def un_sauce(ctx: lb.MessageContext) -> None:
  msg:hikari.Message = ctx.bot.d.pop(ctx.interaction.target_id)

  search_msgs:list[hikari.Message] = []
  del_msgs:list[hikari.Message]    = []

  # Determine which post was clicked by reading the embed data
  if _contains_embed(msg):
    logger.info(f"User {ctx.member.username}#{ctx.member.discriminator} unsauced post {msg.id}.\n\tContent: \"{msg.embeds[0].title}\" - {msg.embeds[0].url}")
    # If we're on the main embed, search the channel history for future replies from the bot, but only if there's more than one image.
    if (msg.embeds[0].fields and msg.embeds[0].fields[0].name == "Image Count"):
      search_msgs = ctx.bot.rest.fetch_messages(channel=msg.channel_id, after=msg.id)
  else:
    logger.info(f"User {ctx.member.username}#{ctx.member.discriminator} unsauced post {msg.id}.\n\tContent: \"{msg}\"")
    # If we're on the image gallery embed, find the response directly before this one
    search_msgs = ctx.bot.rest.fetch_messages(channel=msg.channel_id, before=msg.id)
  
  # If there is another message to remove, find it
  if search_msgs:
    async for m in search_msgs.limit(3):
      # Ensure it's replying to the same message
      if (m.type == hikari.MessageType.REPLY) and (m.referenced_message.id == msg.referenced_message.id):
        del_msgs.append(m)
        break
      logger.warning("Expected to un-sauce other posts, but found none!")

  # Finally, delete both messages
  del_msgs.append(msg)
  for message in del_msgs:
    logger.info(f"Deleting message {message.id}; Parent: {message.referenced_message.id or 'deleted message'}")
    await message.delete()
  if message.referenced_message:
    await msg.referenced_message.delete()

  await ctx.respond(f"Post {msg.id} successfully removed!", flags=hikari.MessageFlag.EPHEMERAL) #(f"Unsauced message: {msg.id}\nReplying to message: {msg.referenced_message.id}", flags=hikari.MessageFlag.EPHEMERAL)

@sauce_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> None:
  logger.warning(f"Caught exception: {type(event.exception)}")

  if isinstance(event.exception, lb.CheckFailure):
    await event.context.respond("\n".join(event.exception.args[0].split(", ")), flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain
  

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
  return links

def _get_extractors(bot: lb.BotApp) -> tuple[Ladle, Pattern]:
    return bot.d.extractors

def _set_extractors(bot: lb.BotApp) -> None:
  l_extractors = config("EXTRACTORS", cast=str).split(",")
  bot.d.extractors = sauce_utils.compile_patterns(sauce_utils.get_ladles(l_extractors))

def _contains_embed(msg: hikari.Message):
  try:
    if msg.embeds[0].title or msg.embeds[0].color:
      # Raw images get inserted as embeds without a title, color, or timestamp
      return True
  except IndexError or ValueError or AttributeError as e:
    return False
  return False

def load(bot: lb.BotApp) -> None:
  _set_extractors(bot)
  logger.debug(f"Loaded extractors: {[(l, e.pattern) for l, e in _get_extractors(bot)]}")
  if bot.d.testmode:
    logger.warning("Loaded in test mode!")
  bot.add_plugin(sauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(sauce_plugin)
