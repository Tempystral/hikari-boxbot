import asyncio
import json
import logging
from re import Match

from aiohttp import ClientSession
from bot.api import ESixApi, EsixApiException
from bot.api.response import SauceResponse, eSixPoolResponse
from hikari import Color

from . import Ladle

logger = logging.getLogger("ladles.esix")

_api = ESixApi()

class ESixPool(Ladle):
  def __init__(self):
    self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'

  async def extract(self, match:Match, session: ClientSession) -> SauceResponse:
    pool_id = match.group("id")
    _api.session = session

    try:
      pool = await _api.get_pool(pool_id)
      posts = await self.__get_pool_images(pool)
      posts = sorted(posts, key=lambda p: p.created_at)
    except EsixApiException as e:
      logger.warning(f"Could not retrieve e621 pool data due to error {e.code}: {e.message} -> {e.data}")
      return

    response = SauceResponse(
      title = f"Pool{': ' + pool.name.replace('_', ' ') if pool.name else None}",
      description = pool.description,
      url = match[0],
      images = [ post.file.url for post in posts ],
      color = Color(0x246cab),
      count = pool.post_count,
      timestamp=pool.created_at
    )
    return response
  
  def __get_pool_images(self, pool: eSixPoolResponse, limit:int = 4):
    return _api.get_posts(pool.post_ids[:limit])
    
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