#!/usr/bin/env python3

import os
from bot import create
from decouple import config

if __name__ == "__main__":
	if os.name != "nt":
			import uvloop
			uvloop.install()

	create(
		config("BOT_TOKEN"),
		config("GUILD", cast=int)
	).run()
