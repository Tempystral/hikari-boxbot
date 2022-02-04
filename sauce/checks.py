import lightbulb
import hikari
#import logging; logger = logging.getLogger()

async def _user_replied_to(context: lightbulb.Context) -> bool:
  msg = await context.bot.rest.fetch_message(context.interaction.channel_id,
                                             context.interaction.target_id)
  if msg.type is not hikari.MessageType.REPLY:
    raise NotAReplyError("This message is not a reply!")
  if not msg.referenced_message.author == context.author:
    raise NotCallingAuthorError("Only the original poster or a mod can remove this post.")
    #logger.warning(f"Referenced message: {msg.referenced_message.id}, Author: {msg.referenced_message.author}")
    #logger.warning(f"Selected message: {context.interaction.target_id}, Author: {context.author}")
  return True

user_replied_to = lightbulb.Check(p_callback=_user_replied_to, m_callback=_user_replied_to)

'''async def _reply_only(context: lightbulb.Context) -> bool:
  if context.interaction.type == hikari.InteractionType.APPLICATION_COMMAND:
    msg = await context.bot.rest.fetch_message(context.interaction.channel_id,
                                               context.interaction.target_id)
    if msg.type is not hikari.MessageType.REPLY:
      raise lightbulb.errors.CheckFailure("This command can only be used on BoxBot replies.")
    return True

reply_only = lightbulb.Check(p_callback=_reply_only, m_callback=_reply_only)'''

class NotAReplyError(lightbulb.errors.CheckFailure):
  """
  The message selected by the calling check is not a reply.
  """

class NotCallingAuthorError(lightbulb.errors.CheckFailure):
  """
  The calling user is not the user of the original sauced message.
  """