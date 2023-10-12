import asyncio
import json
from re import Match
from typing import Dict

from aiohttp import ClientSession, BasicAuth
from decouple import config
from hikari import Color
from sauce.ladles.abc import LadleException
from sauce.response import SauceResponse
from sauce.response import eSixPoolResponse

from . import Ladle
import logging

logger = logging.getLogger("ladles.esix")

class ESixApi:
  def __init__(self):
    self._auth = BasicAuth(
      config("E621_USER", cast=str),
      config("E621_KEY", cast=str)
    )
    self._base_url = 'https://e621.net'
    self._request_count = 0
    self.sleep_timer = 0

  async def get(self, url: str, session: ClientSession) -> Dict:
    await asyncio.sleep(self.sleep_timer)
    req_url = self._base_url + url
    async with session.get(req_url, headers={'User-Agent': 'sauce/0.1'}, auth=self._auth) as response:
      text = await response.read()
      result:dict = json.loads(text)
      #logger.debug(result)
      if result.get("success"):
        raise EsixApiException(code=result["code"], message=result["message"], data=result)

    self.sleep_timer = 0.5
    return result


_api = ESixApi()


class ESixPool(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    pool_id = match.group("id")

    try:
      data = await _api.get(f'/pools/{pool_id}.json', session)
      esix_pool = eSixPoolResponse(**data)
      first_post = await _api.get(f'/posts/{esix_pool.post_ids[0]}.json', session)
    except EsixApiException as e:
      logger.warning(f"Could not retrieve e621 pool data due to error {e.code}: {e.message} -> {e.data}")
      return

    response = SauceResponse(
      title = f"Pool{': ' + esix_pool.name.replace('_', ' ') if esix_pool.name else None}",
      description = esix_pool.description,
      url = match[0],
      image = first_post['post']['file']['url'],
      color = Color(0x246cab),
      count = esix_pool.post_count
    )
    return response
    
  async def cleanup(self, match:Match) -> None:
      pass

"""class ESixPost(BaseInfoExtractor):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e621|e926)\.net/posts/(?P<id>\d+)'

  async def extract(self, url: str, session: ClientSession) -> Optional[Dict]:
    groups = re.match(self.pattern, url).groupdict()
    post_id = groups['id']

    data = await _api.get(f'/posts/{post_id}.json', session)
    post = data['post']
    tags = post['tags']['general']
    #print(data)
    
    # Determine if post is embed-blacklisted
    blacklisted = any([tag in tags for tag in ['loli', 'shota']])
    blacklisted = blacklisted or ('young' in tags and not post['rating'] == 's')
    if blacklisted:
      images = {'images': [post['file']['url']]}
      if post['file']['ext'] in ['webm']:
        return images
      if post['file']['ext'] in ['jpg', 'png', 'gif']:
        characters = post["tags"]["character"]
        artists = post["tags"]["artist"]
        title = f"{commaList(characters)} drawn by {commaList(artists)}"
        return {'url': url, 'title': title, 'description': post["description"], 'images': [post['file']['url']]}


class ESixDirectLink(Ladle):
  '''Extractor to source E621 and E926 direct image links'''
  def __init__(self):
    self.pattern = r'https?://static1\.(?P<site>e621|e926)\.net/data/(sample/)?../../(?P<md5>\w+)\..*'

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    image_md5 = match.group("md5")
    data = await _api.get('/posts.json?tags=md5%3A' + image_md5, session)
    post_url = "https://e621.net/posts/" + str(data['posts'][0]['id'])
    response = SauceResponse(
      url=post_url,
      description = data["description"],

    )
    return response"""
      
'''
artists = [data["artist"][k] for k in data["artist"].keys()]
return {'name': ", ".join([a.capitalize() for a in artists if a != "conditional_dnp"]),
    'description': data.get('description'),
    'images': urls,
    'count': data['post_count']
    }
'''


class EsixApiException(LadleException):
  """
  The exception to throw when there is a problem retrieving data from e621.net
  """