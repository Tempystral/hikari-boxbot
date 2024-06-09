import logging

import hikari
from aiohttp import ClientSession
from decouple import config
from lightbulb import BotApp

from bot.utils import bot_utils, loghelper
from bot.utils.config.serverConfig import get_settings

logger = logging.getLogger("BoxBot")

class BoxBot(BotApp):
  def __init__(self, token:str, *guilds:int, log_level:str = "DEBUG"):
    self.token = token
    self.guilds = guilds
    super().__init__(token=self.token,
                     prefix="!",
                     intents=hikari.Intents.ALL_GUILDS | hikari.Intents.MESSAGE_CONTENT,
                     default_enabled_guilds=guilds,
                     banner="bot",
                     logs=log_level
                    )
    loghelper.setup_logging(log_level, "./logs/boxbot.log")

  async def on_starting(self, event:hikari.Event) -> None:
    logger.info("Starting...")
    self.d.settings = get_settings()
    self.d.aio_session = ClientSession()
    self.d.test_channel = config("TEST_CHANNEL", cast=int)
    self.d.emojis = await bot_utils.get_emoji(self, self.guilds)
  
  async def on_started(self, event:hikari.StartedEvent) -> None:
    user = self.get_me()
    guilds = "\n\t".join([f"{g.name} [{g.id}]" async for g in self.rest.fetch_my_guilds()])
    if user:
      logger.info(f"Logged in as: {user} with ID: {user.id}")
    logger.info(f"Logged into guilds:\n\t{guilds}")

  async def on_stopping(self, event:hikari.Event) -> None:
    logger.info("Shutting down...")
    await self.d.aio_session.close()

def create(token:str, guild_id:int, log_level:str) -> BoxBot:
  bot = BoxBot(token, guild_id, log_level=log_level) # init
  # Listen for system events
  bot.subscribe(hikari.StartingEvent, bot.on_starting)
  bot.subscribe(hikari.StartedEvent, bot.on_started)
  bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
  # Load extensions
  bot.load_extensions_from("./bot/modules/", must_exist=False)
  return bot
