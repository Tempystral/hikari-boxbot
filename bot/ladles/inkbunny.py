import re, json
from aiohttp import ClientSession
from scalpl import Cut
from hikari import Color
from decouple import config
from re import Match
import logging

from bot.api.response import SauceResponse
from bot.utils.mlstripper import strip_tags
from . import Ladle

logger = logging.getLogger("InkBunny")

class InkBunny(Ladle):
  def __init__(self):
    self.pattern = r'https?://.*inkbunny\.net/s/(?P<id>\d+)'
    self.__sid = "" # Cannot start as None or else requests fail-unsafe

  async def _login(self, session: ClientSession) -> None:
    user_info = {
      "username" : config("IB_USER", cast=str),
      "password" : config("IB_PASS", cast=str)
    }
    logger.info(f"Logging into InkBunny as user {user_info['username']}")
    async with session.get(url='https://inkbunny.net/api_login.php', params = user_info, headers = {'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      try:
        self.__sid = data["sid"]
        logger.info(f"Obtained SID <{self.__sid}> from Inkbunny")
      except KeyError as e:
        logger.critical(f'Could not login to InkBunny:\nResponse from server: {data["error_message"]}')

  async def extract(self, match: re.Match, session: ClientSession) -> SauceResponse:
    if not self.__sid:
      await self._login(session)
    
    params = {
      "sid" : self.__sid,
      "submission_ids" : match.group("id"),
      "show_description_bbcode_parsed" : "yes"
    }

    request_url = 'https://inkbunny.net/api_submissions.php'
    async with session.get(request_url, params=params, headers={'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      logger.debug(data)
      if "error_code" in data:
        if int(data["error_code"]) == 2:
          logger.warning("Logged out; Retrying...")
          await self._login(session) # Refresh SID
          await self.extract(match, session)
      else:
        submission = Cut(data["submissions"][0])

        response = SauceResponse(
          title = submission.get("title"),
          description=strip_tags(submission.get("description_bbcode_parsed")),
          url=match[0],
          images = [f.get("file_url_full") for f in submission.get("files")],
          author_name = submission.get("username"),
          author_icon = submission.get("user_icon_url_small") or r'https://qc.ib.metapix.net/images78/usericons/large/noicon.png',
          author_url = f"https://www.inkbunny.net/{submission.get('username')}",
          color = Color(0x73d216),
          timestamp=submission.get("create_datetime")
        )
        return response
              
  async def cleanup(self, match:Match) -> None:
    pass