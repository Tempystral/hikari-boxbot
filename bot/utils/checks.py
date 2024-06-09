import logging

import lightbulb as lb
from hikari import InteractionType, Message, MessageType

from bot.utils.config.serverConfig import ServerConfig

logger = logging.getLogger("BoxBot.sauce.checks")

async def _user_replied_to(context: lb.Context) -> bool:
  msg:Message = await get_message_in_datastore(context)
  if not msg.referenced_message:
    return True
  try:
    if not msg.referenced_message.author == context.author:
      context.bot.d.pop(msg.id)
      raise NotCallingAuthorError("Only the original poster or a mod can remove this post.")
  except AttributeError as e:
    pass # This should be ignored because it's optional AND getting checked again in reply_only
  return True

async def _elevated_user(context: lb.Context) -> bool:
  if (guild := context.get_guild()):
    user = guild.get_member((await context.author.fetch_self()).id)
    settings: ServerConfig = context.bot.d.settings
    try:
      for role in settings.get_guild(guild.id).elevated_roles:
        if role in user.role_ids:
          return True
    except AttributeError as e:
      pass
  raise NotElevatedError("User must have an elevated role to perform this command!")

async def _reply_only(context: lb.Context) -> bool:
  if context.interaction.type == InteractionType.APPLICATION_COMMAND:
    msg:Message = await get_message_in_datastore(context)
    if msg.type is not MessageType.REPLY:
      context.bot.d.pop(msg.id)
      raise NotAReplyError("This command can only be used on replies.")
    return True

def _on_bot_message(context: lb.Context) -> bool:
  if context.interaction.type == InteractionType.APPLICATION_COMMAND:
    #logger.info(f"Context Author: {context.author}\nContext Member: {context.member}\nContext User: {context.user}\nContext Options Target: {context.options.target}")
    msg:Message = context.options.target
    if not msg.author.is_bot:
      raise BotMessageOnlyError("This command can only be run on messages sent by a bot.")
    return True

async def get_message_in_datastore(context: lb.Context) -> bool:
  msg = context.bot.d.get(context.interaction.target_id)
  return (msg
          if msg
          else context.bot.d.setdefault(context.interaction.target_id,
                                        await _get_message(context))
  ) # If we already have a message ID saved, don't get it again to avoid the rate limit

async def _get_message(context: lb.Context) -> bool:
  logger.debug("Fetching message from Discord...")
  return await context.bot.rest.fetch_message(context.interaction.channel_id,context.interaction.target_id)


user_replied_to = lb.Check(p_callback=_user_replied_to, m_callback=_user_replied_to)
"""Only run command on messages which are a reply to the calling user."""
reply_only = lb.Check(p_callback=_reply_only, m_callback=_reply_only)
"""Only run command on messages marked with message flag 19 [`REPLY`]."""
on_bot_message = lb.Check(p_callback=_on_bot_message, m_callback=_on_bot_message)
"""Only run command on messages sent by a bot."""
elevated_user = lb.Check(p_callback=_elevated_user, m_callback=_elevated_user)
"""Only run command if the user has an elevated role."""

class CheckFailureWithData(lb.errors.CheckFailure):
  """A wrapper class for errors containing cleanup data."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args)
    self.data = kwargs.get("data")

class NotAReplyError(lb.errors.CheckFailure):
  """The message selected by the calling check is not a reply."""

class NotCallingAuthorError(lb.errors.CheckFailure):
  """The calling user is not the user of the original sauced message."""

class BotMessageOnlyError(lb.errors.CheckFailure):
  """An error raised when a command intended for bot messages was run on a non-bot message."""

class NotElevatedError(lb.errors.CheckFailure):
  """An error raised when a command is run by non-elevated users message."""
