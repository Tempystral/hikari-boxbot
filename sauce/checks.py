import lightbulb
import hikari
#import logging; logger = logging.getLogger()

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
      raise lightbulb.errors.CheckFailure("This command can only be used on BoxBot replies.")
    return True

user_replied_to = lightbulb.Check(p_callback=_user_replied_to, m_callback=_user_replied_to)
reply_only = lightbulb.Check(p_callback=_reply_only, m_callback=_reply_only)

class NotAReplyError(lightbulb.errors.CheckFailure):
  """
  The message selected by the calling check is not a reply.
  """

class NotCallingAuthorError(lightbulb.errors.CheckFailure):
  """
  The calling user is not the user of the original sauced message.
  """