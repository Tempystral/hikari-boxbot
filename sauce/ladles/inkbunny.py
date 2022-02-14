import aiohttp, json, re, scalpl
from hikari import Color
from decouple import config
from re import Match
import logging

from sauce.response import SauceResponse
from . import Ladle

logger = logging.getLogger("InkBunny")

class InkBunny(Ladle):
  def __init__(self):
    self.pattern = r'https?://.*inkbunny\.net/s/(?P<id>\d+)'
    #self.hotlinking_allowed = True
    self.__sid = "" # Cannot start as None or else requests fail-unsafe

  async def _login(self, session: aiohttp.ClientSession) -> None:
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

  async def extract(self, match: re.Match, session: aiohttp.ClientSession) -> SauceResponse:
    if not self.__sid:
      await self._login(session)
    
    params = {
      "sid" : self.__sid,
      "submission_ids" : match.group("id")
    }

    request_url = 'https://inkbunny.net/api_submissions.php'
    async with session.get(request_url, params=params, headers={'User-Agent': 'sauce/0.1'}) as response:
      text = await response.read()
      data = json.loads(text)
      if "error_code" in data:
        if int(data["error_code"]) == 2:
          logger.warning("Logged out; Retrying...")
          await self._login(session) # Refresh SID
          await self.extract(match, session)
      else:
        submission = scalpl.Cut(data["submissions"][0])

        response = SauceResponse(
          title = submission.get("title"),
          description=None,
          url=match[0],
          images = [f.get("file_url_full") for f in submission.get("files")],
          author_name = submission.get("username"),
          author_icon = submission.get("user_icon_url_small") or r'https://qc.ib.metapix.net/images78/usericons/large/noicon.png',
          author_url = f"https://www.inkbunny.net/{submission.get('username')}",
          color = Color(0x73d216)
        )
        return response
              
  async def cleanup(self, match:Match) -> None:
    pass