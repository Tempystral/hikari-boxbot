import logging
import hikari
from aiohttp import ClientSession
from lightbulb import BotApp
from utils import loghelper

logger = logging.getLogger("BoxBot")

class BoxBot(BotApp):
  def __init__(self, token:str, guilds:str, log_level:str = "DEBUG"):
    self.token = token
    self.guilds = guilds
    super().__init__(token=self.token,
                     prefix="!",
                     intents=hikari.Intents.ALL_GUILDS | hikari.Intents.MESSAGE_CONTENT,
                     default_enabled_guilds=guilds,
                     banner="bot",
                     logs=log_level
                    )
    loghelper.setup_logging(log_level)

  async def on_starting(self, event:hikari.Event) -> None:
    logger.info("Starting...")
    self.d.aio_session = ClientSession()
  
  async def on_started(self, event:hikari.Event) -> None:
    logger.info(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
    logger.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

  async def on_stopping(self, event:hikari.Event) -> None:
    logger.info("Shutting down...")
    await self.d.aio_session.close()

def create(token:str, guild_id:str, log_level:str) -> BoxBot:
  bot = BoxBot(token, guild_id, log_level) # init
  # Listen for system events
  bot.subscribe(hikari.StartingEvent, bot.on_starting)
  bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
  # Load extensions
  bot.load_extensions_from("./modules/", must_exist=False)
  return bot
