import hikari
import lightbulb as lb

sauce_plugin = lb.Plugin("Sauce")

@sauce_plugin.listener(hikari.GuildMessageCreateEvent)
async def sauce(event: hikari.GuildMessageCreateEvent):
  if (event.content == "Ping!"):
    await event.get_channel().send("Pong!")
  # Perform a regex match on a url

  # If the regex finds a suitable match, send the link to one of the ladles to retrieve metadata

  # Once metadata is retrieved, send it off to the embed generator

  # Post the embed + message


def load(bot: lb.BotApp) -> None:
  bot.add_plugin(sauce_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(sauce_plugin)