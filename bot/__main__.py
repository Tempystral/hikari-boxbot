#!/usr/bin/env python3

import asyncio
import os

from decouple import config

from bot import create

if __name__ == "__main__":
	if os.name != "nt":
			import uvloop
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
	token = config("BOT_TOKEN", cast=str)
	log_level = config("LOG_LEVEL", cast=str)
	create(token, log_level).run()
