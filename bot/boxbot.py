import aiohttp
import hikari
import lightbulb
import logging

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

    async def on_starting(self, event:hikari.Event) -> None:
        logger.info("Starting...")
        self.d.aio_session = aiohttp.ClientSession()
    
    async def on_started(self, event:hikari.Event) -> None:
        logger.info(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
        logger.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

    async def on_stopping(self, event:hikari.Event) -> None:
        logger.info("Shutting down...")
        await self.d.aio_session.close()

def create(token:str, guild_id:str) -> BoxBot:
    bot = BoxBot(token, guild_id) # init
    # Listen for system events
    bot.subscribe(hikari.StartingEvent, bot.on_starting)
    bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
    # Load extensions
    bot.load_extensions_from("./modules/", must_exist=False)
    return bot