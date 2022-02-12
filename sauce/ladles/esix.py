import asyncio
import json
from re import Match
from typing import Dict, Optional

import aiohttp
from decouple import config
from hikari import Color
from sauce.ladles.abc import LadleException
from sauce.response import SauceResponse

from . import Ladle
import logging

logger = logging.getLogger("ladles.esix")

class ESixApi:
    def __init__(self):
        self._auth = aiohttp.BasicAuth(
            config("E621_USER", cast=str),
            config("E621_KEY", cast=str)
        )
        self._base_url = 'https://e621.net'
        self._request_count = 0
        self._sleep = asyncio.sleep(0)

    async def get(self, url: str, session: aiohttp.ClientSession) -> Dict:
        await self._sleep
        req_url = self._base_url + url
        async with session.get(req_url, headers={'User-Agent': 'sauce/0.1'}, auth=self._auth) as response:
            text = await response.read()
            result:dict = json.loads(text)
            #logger.debug(result)
            if result.get("success"):
                raise EsixApiException(code=result["code"], message=result["message"], data=result)

        self._sleep = asyncio.get_event_loop().create_task(asyncio.sleep(0.5))
        return result


_api = ESixApi()


class ESixPool(Ladle):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, match:Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        pool_id = match.group("id")

        data = await _api.get(f'/pools/{pool_id}.json', session)
        first_post = await _api.get(f'/posts/{data["post_ids"][0]}.json', session)
        data_title:str = data.get("name")

        response = SauceResponse(
            title=f"Pool{': ' + data_title.replace('_', ' ') if data_title else None}",
            description=data.get("description"),
            url=match[0],
            image=first_post['post']['file']['url'],
            colour = Color(0x246cab),
            count = data.get("post_count")
        )
        return response
        

"""
class ESixPost(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/posts/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
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


class ESixDirectLink(BaseInfoExtractor):
    '''Extractor to source E621 and E926 direct image links'''
    def __init__(self):
        self.pattern = r'https?://static1\.(?P<site>e621|e926)\.net/data/(sample/)?../../(?P<md5>\w+)\..*'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        image_md5 = re.match(self.pattern, url).groupdict()['md5']
        data = await _api.get('/posts.json?tags=md5%3A' + image_md5, session)
        post_url = "https://e621.net/posts/" + str(data['posts'][0]['id'])
        return {'images': [post_url]}
            
        '''
        artists = [data["artist"][k] for k in data["artist"].keys()]
        return {'name': ", ".join([a.capitalize() for a in artists if a != "conditional_dnp"]),
                'description': data.get('description'),
                'images': urls,
                'count': data['post_count']
                }
        '''
"""

class EsixApiException(LadleException):
    """
    The exception to throw when there is a problem retrieving data from e621.net
    """