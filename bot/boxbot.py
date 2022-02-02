from pathlib import Path
import hikari
import lightbulb
import logging
#from utils import boxconfig, logger

logger = logging.getLogger("BoxBot")

class BoxBot(lightbulb.BotApp):
    def __init__(self, token:str, guilds:str):
        self.token = token
        self.guilds = guilds
        super().__init__(token=self.token,
                         prefix="!",
                         intents=hikari.Intents.ALL_GUILDS,
                         default_enabled_guilds=guilds,
                         
                         banner="bot")

    def on_starting(self) -> None:
        logger.info("Starting...")
    
    def on_started(self) -> None:
        logger.info(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
        logger.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

    def on_stopping(self) -> None:
        logger.info("Shutting down...")

def create(token:str, guild_id:str) -> BoxBot:
    bot = BoxBot(token, guild_id)
    bot.load_extensions_from("./extensions/", must_exist=False)
    return bot