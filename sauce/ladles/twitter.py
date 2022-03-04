from re import Match
from hikari import Color
from tweepy import Client, User, Media, Tweet
import aiohttp
from decouple import config
from sauce import SauceResponse

from . import Ladle

from logging import getLogger

logger = getLogger("ladles.twitter")

class Twitter(Ladle):
    def __init__(self):
        self.pattern = r'https?://(?:mobile\.)?twitter\.com/[a-zA-Z0-9_]+/status/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, match: Match, session: aiohttp.ClientSession) -> SauceResponse:
        client = Client(config("TWITTER_BEARER"))
        tweet_id = match.group("id")

        data = client.get_tweet(id = tweet_id,
                                user_auth = False,
                                expansions = ["attachments.media_keys", "author_id"],
                                media_fields = ["media_key", "alt_text", "url", "type"],
                                tweet_fields = ["attachments", "author_id", "text"],
                                user_fields = ["url", "username", "profile_image_url"]
                                )
        tweet:Tweet = data.data
        user:User = data.includes["users"][0]
        media:list[Media] = data.includes["media"]
        
        response = SauceResponse(
            title = None,
            description = tweet.text,
            url = None,
            author_name = user.username,
            author_url = user.url,
            author_icon = user.profile_image_url,
            images = [m.url for m in media],
            colour = Color(0x1d9bf0)
        )

        return response



    async def cleanup(self, match:Match):
        pass