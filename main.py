#!/usr/bin/env python3

import os
import asyncio
from bot import create
from decouple import config

if __name__ == "__main__":
	if os.name != "nt":
			import uvloop
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
	create(
		config("BOT_TOKEN"),
		config("GUILD", cast=int),
		config("LOG_LEVEL", cast=str)
	).run()
