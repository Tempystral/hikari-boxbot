import logging
import re
from io import BytesIO
from typing import Tuple
from aiohttp import ClientSession
from hikari import Resourceish

import bot.ladles

logger = logging.getLogger("Boxbot.sauce.util")

def remove_spoilered_text(message:str) -> str:
  '''Quick hacky way to remove spoilers, doesn't handle ||s in code blocks'''
  strs = message.split('||')
  despoilered = ''.join(strs[::2]) # Get every 4th string
  despoilered += strs[-1] if len(strs) % 2 == 0 else ''
  return despoilered

def get_ladles(l_ladles:list[str]) -> list[bot.ladles.Ladle]:
  return [getattr(bot.ladles, name.strip())() for name in l_ladles]

def compile_patterns(l_ladles:list[bot.ladles.Ladle]) -> list[Tuple[bot.ladles.Ladle, re.Pattern]]:
  return [(ladle, re.compile(ladle.pattern)) for ladle in l_ladles]

async def get_filesize(url:str, session: ClientSession):
  """
  Retrieves the size of a file on the internet. Returns -1 if the request fails, otherwise returns size in bytes.

  url (`str`): The target resource
  
  session (`aiohttp.Session`) A web session to make the call with
  """
  try:
    async with session.head(url) as response:
      logger.debug(f"Size of {url}: {response.content_length / 1024}KiB")
      return response.content_length
  except AttributeError as e:
    return -1

async def check_file_sizes(urls:list[Resourceish], limit:int, session:ClientSession):
  for url in urls:
    if isinstance(url, BytesIO):
      if url.__sizeof__() > limit:
        return False
    if isinstance(url, str):
      if await get_filesize(url, session) > limit:
        return False
  return True