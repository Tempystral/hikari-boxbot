import asyncio
from logging import getLogger
from decouple import config
import lightbulb
from lightbulb.ext import tasks
from utils import BoardWatcher
from utils.fourchanaio import Chan, Post

logger = getLogger("Boxbot.modules.watcher")

plugin = lightbulb.Plugin("Watcher")

watcher:BoardWatcher = None

@tasks.task(m=5)
async def check_threads():
  threads = await get_new_threads()
  if threads:
    urls = [thread.url for thread in threads]
    msg = ("Found {n} new threads{s}:\n{ts}"
            .format(n = len(urls), s = "s"*int(bool(len(urls))), ts="\n".join(urls)))
    plugin.bot.rest.create_message(content=msg,
                                  channel=plugin.bot.d.notify_channel,
                                  role_mentions=plugin.bot.d.notify_role)

async def get_new_threads() -> list[Post]:
  threads = await watcher.update()
  return threads

def load(bot: lightbulb.BotApp) -> None:
  global watcher
  watcher = BoardWatcher(chan = Chan(session = bot.d.aio_session),
                         search_patterns = config("WATCHER_PATTERN"),
                         regex = config("WATCHER_REGEX"))
  bot.d.notify_channel = config("WATCHER_NOTIFY_CHANNEL", cast=int)
  bot.d.notify_role = config("WATCHER_NOTIFY_ROLE", cast=int)
  bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
  asyncio.run(watcher.close())
  bot.remove_plugin(plugin)
