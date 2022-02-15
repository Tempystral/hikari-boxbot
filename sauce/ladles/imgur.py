import json
from re import Match
from typing import Dict, Optional

import aiohttp
import scalpl

from . import Ladle
import logging

logger = logging.getLogger("ladles.imgur")

class Imgur(Ladle):
    def __init__(self):
        self.pattern = r'https?://(www\.)?imgur\.com/(?:a|gallery)/(?P<id>\w+)'
        self.hotlinking_allowed = True

    async def extract(self, match:Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        gallery_id = match.group("id")
        request_url = 'https://api.imgur.com/3/album/' + gallery_id
        headers = {'User-Agent': 'sauce/0.1',
                   "Authorization": "Client-ID " + boxconfig.get("imgur.clientid")}

        async with session.get(request_url, headers=headers) as response:
            text = await response.read()
            album = scalpl.Cut(json.loads(text))
            if not album:
                return
            if album.get("success"):
                count = len(album["data.images"])
                if count == 1:
                    album_images = [] #[album["data.images[0].link"]]
                else:
                    album_images = [img["link"] for img in album["data.images"][1:]]

                return {'images': album_images,
                        #"title": album.get("title"),
                        #"description": album.get("description"),
                        "count": count
                        }
            else:
                logger.warning(f"Cannot retrieve album with ID {gallery_id}: {album.get('data.error')}")