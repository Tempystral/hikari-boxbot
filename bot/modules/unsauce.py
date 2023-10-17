import logging
from re import T

import hikari
import lightbulb as lb
from bot.api.exception import LadleException
from bot.utils.checks import on_bot_message, reply_only, user_replied_to
from decouple import config

from bot.utils.sauce_utils import contains_embed

logger = logging.getLogger("BoxBot.modules.unsauce")

unsauce_plugin = lb.Plugin("Unsauce")

@unsauce_plugin.command
@lb.add_checks(on_bot_message, reply_only)
@lb.add_checks(user_replied_to | lb.has_roles(role1=config("ELEVATED_ROLES", cast=int)))
@lb.command("Un-Sauce", "Purge the last message BoxBot sauced for you.")
@lb.implements(lb.MessageCommand)
async def un_sauce(ctx: lb.MessageContext) -> None:
  msg:hikari.Message = ctx.bot.d.pop(ctx.interaction.target_id)

  search_msgs = None
  del_msgs:list[hikari.Message]    = []

  # Determine which post was clicked by reading the embed data
  if contains_embed(msg):
    logger.info(f"User {ctx.member.username}#{ctx.member.discriminator} unsauced post {msg.id}.\n\tContent: \"{msg.embeds[0].title}\" - {msg.embeds[0].url}")
    # If we're on the main embed, search the channel history for future replies from the bot, but only if there's more than one image.
    if __has_prior_message(msg):
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

def __has_prior_message(msg: hikari.Message):
  '''Determine whether there is a previous message to delete'''
  if msg.embeds[0].fields and msg.embeds[0].fields[0].name == "Image Count":
    return True
  return False

@unsauce_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> None:
  logger.warning(f"Caught exception: {type(event.exception)}")

  if isinstance(event.exception, lb.CheckFailure):
    await event.context.respond(content="\n".join(event.exception.args[0].split(", ")),
                                flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain
  
  elif isinstance(event.exception, LadleException):
    await event.context.respond(content=f"Could not sauce post for the following reason: {event.exception.message}",
                                flags=hikari.MessageFlag.EPHEMERAL)
    return True

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(unsauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(unsauce_plugin)
