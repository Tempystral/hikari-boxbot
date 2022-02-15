from re import Match
from decouple import config

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from . import Ladle
from sauce import SauceResponse


class Furaffinity(Ladle):
  def __init__(self):
    self.pattern = r'https?://www.furaffinity.net/(?:view|full)/(?P<id>\d+)'
    self._cookie = config("FA_COOKIE")

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    submission_id = match.group("id")

    url = f'http://www.furaffinity.net/view/{submission_id}'
    async with session.get(url, headers={'Cookie': self._cookie}) as response:
      text = await response.read()
      soup = BeautifulSoup(text, "html.parser")

      title, _, author = soup.find('meta', property='og:title')['content'].rpartition(" by ")
      icon_url = 'https:' + soup.select('.classic-submission-title img.avatar')[0]['src']

      description = soup.select('.maintable .maintable tr:nth-of-type(2) td')[0].get_text()
      description = '\n'.join([l for l in description.split('\n') if l])
      description = (description[:197] + '...') if len(description) > 200 else description

      rating = soup.find('meta', attrs={'name': 'twitter:data2'})['content']

      img = 'https:' + soup.select('#submissionImg')[0]['data-fullview-src']

      if rating == "General":
        return None
      return SauceResponse(title=title, description=description, url=url, author_name=author, author_icon=icon_url, image=img)
      
      #{'url': url, 'name': author, 'icon_url': icon_url, 'title': title, 'description': description, 'images': [img]}

  async def cleanup(self, match:Match) -> None:
    pass