from pathlib import Path
import hikari
import tanjun
from logging import Logger
#from utils import boxconfig, logger

logger = Logger("logger")

# BoxBot extends commands.Bot, which extends discord.Client
class BoxBot(hikari.GatewayBot):
    def __init__(self, token:str):
        #self.config = boxconfig.config
        self.token = token
        super().__init__(token=self.token,
                         intents=hikari.Intents.ALL_GUILDS,
                         banner="bot")

    def on_starting(self) -> None:
        logger.info("Starting...")
    
    def on_started(self) -> None:
        logger.info(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
        logger.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

    def on_stopping(self) -> None:
        logger.info("Shutting down...")

def create(token:str, guild_id:str) -> BoxBot:
    bot = BoxBot(token)
    client = tanjun.Client.from_gateway_bot(bot, set_global_commands=guild_id)
    client.load_modules(*Path("./modules").glob("*.py"))
    return bot
