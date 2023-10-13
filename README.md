# Boxbot 2.0
  A discord bot using [hikari]() for sourcing images from Discord-unfriendly websites.

  Boxbot was intended as a replacement to [SauceBot](https://github.com/JeremyRuhland/saucebot-discord) - other solutions have cropped up since Boxbot's creation, but at the time the first version was written, there were no good alternatives.
## Installation
### Requirements
Python >= `3.11.x`
### Steps
1. (Optional) Set up a virtual environment: `python3.11 -m venv env; source env/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. (Optional) Run in a virtual terminal. I like tmux: `tmux new-session -n boxbot`
4. Run the bot. Optimizations are recommended: `python -O -m bot`
## Config File
```env
# Token for your discord bot
BOT_TOKEN=
# ID for your discord guild
GUILD=
# ID for the channel used by the threadwatcher
NOTIFICATION_CHANNEL=
# ID for test channel
TEST_CHANNEL=
# ID for elevated roles. These roles will be able to un-sauce any message, even ones not from themselves.
ELEVATED_ROLES=
# Path to a cache dir for pixiv
CACHE= 
LOG_LEVEL=DEBUG

EXTRACTORS=Furaffinity,InkBunny,ESixPool,Pixiv,EHentai,XTwitter # Class names for ladles, enable or disable as necessary

# Ladle Settings
E621_USER=
E621_KEY=

# A cookie from an authenticated session
FA_COOKIE= 

IB_USER=
IB_PASS=
# Follow these steps to get a refresh token: https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
PIXIV_REFRESH_TOKEN = 
```
## Feature: Source Embedding ("Sauce")
  Boxbot replaces much of the functionality of SauceBot, and extends its features to include more websites. Components are maintained through extensions called "ladles".
### Twitter (via FxTwitter)
- FxTwitter somehow has a functional API, meaning tweets are consistently sourced and embedded regardless of host (x.com vs twitter.com) or media.
- Up to four images are embedded with a tweet, and videos are supplied in the same message if applicable.
### Pixiv
  - Posts and albums are embedded with a preview of up to 4 images.
  - ~~Ugoira does not work at this time (January 2020).~~
	  - Ugoira does work now! Much thanks to [altbdoor](https://github.com/altbdoor/py-ugoira) for their command-line tool I ripped apart and frankensteined back together for this.
### Furaffinity
  - The default embedder works fine, so only explicit posts are sauced. Posts are embedded with submission info and an image.
  - **Note: The account you use for this must be using the old site theme.**
### e621/e926
  - Links to pools are sourced with a description and up to four preview images.
### Inkbunny
  - Albums are embedded with a description and previews.
  - Mature or Explicit links are handled for users who are not logged in.
### E-Hentai Galleries
  - Gallery links and individual pages are sourced back to the original gallery page.
  - ExHentai links are sourced back to e-hentai when possible.
	  - If certain tags would cause the gallery to be filtered on the public site, a warning is displayed in the embed.
### Planned Ladles
  - Weasyl
  - Newgrounds
### Deprecated:
#### Imgur
  - ~~Multi-image albums are embedded with a description and previews.~~
  - ~~Sound from Imgur videos does not work due to their unique implementation of webm.~~
## Feature: Threadwatcher
  - Boxbot automatically searches for 4chan threads according to tags you set. **2023: This feature may or may not work.**
  - Threadwatcher will post in a specific channel and update a specific role when posts are made.
  - For example, Boxbot can periodically search for threads containing the text "Mao Mao" from /co/ and post them to an announcement channel, notifying a "Cartoon Fans" role upon update. 
  - This feature is optional.
