#!/usr/bin/env python3

import asyncio
import os

from decouple import config

from bot import create

if __name__ == "__main__":
	if os.name != "nt":
			import uvloop
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
	create(
		config("BOT_TOKEN"),
		config("LOG_LEVEL", cast=str)
	).run()
