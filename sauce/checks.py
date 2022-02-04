import lightbulb
import hikari
import logging

logger = logging.getLogger("BoxBot.sauce.checks")

async def _user_replied_to(context: lightbulb.Context) -> bool:
  msg = await context.bot.rest.fetch_message(context.interaction.channel_id,
                                             context.interaction.target_id)
  try:
    if not msg.referenced_message.author == context.author:
      raise NotCallingAuthorError("Only the original poster or a mod can remove this post.")
  except AttributeError as e:
    pass # This should be ignored because it's optional AND getting checked again in reply_only
  return True

async def _reply_only(context: lightbulb.Context) -> bool:
  if context.interaction.type == hikari.InteractionType.APPLICATION_COMMAND:
    msg = await context.bot.rest.fetch_message(context.interaction.channel_id,
                                               context.interaction.target_id)
    if msg.type is not hikari.MessageType.REPLY:
      raise lightbulb.errors.CheckFailure("This command can only be used on replies.")
    return True

def _on_bot_message(context: lightbulb.Context) -> bool:
  if context.interaction.type == hikari.InteractionType.APPLICATION_COMMAND:
    #logger.info(f"Context Author: {context.author}\nContext Member: {context.member}\nContext User: {context.user}\nContext Options Target: {context.options.target}")
    msg:hikari.Message = context.options.target
    if not msg.author.is_bot:
      raise BotMessageOnlyError("This command can only be run on messages sent by a bot.")
    return True

user_replied_to = lightbulb.Check(p_callback=_user_replied_to, m_callback=_user_replied_to)
"""
Only run command on messages which are a reply to the calling user.
"""

reply_only = lightbulb.Check(p_callback=_reply_only, m_callback=_reply_only)
"""
Only run command on messages marked with message flag 19 [`REPLY`].
"""

on_bot_message = lightbulb.Check(p_callback=_on_bot_message, m_callback=_on_bot_message)
"""
Only run command on messages sent by a bot.
"""

class NotAReplyError(lightbulb.errors.CheckFailure):
  """
  The message selected by the calling check is not a reply.
  """

class NotCallingAuthorError(lightbulb.errors.CheckFailure):
  """
  The calling user is not the user of the original sauced message.
  """

class BotMessageOnlyError(lightbulb.errors.CheckFailure):
  """
  An error raised when a command intended for bot messages was run on a non-bot message.
  """