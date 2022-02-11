from typing import Optional
from hikari import Resourceish

from hikari.embeds import Embed

class SauceResponse():
  '''
  A response object containing all the contents required for an embed.
  '''
  def __init__(self,
               title : Optional[str] = None,
               description : Optional[str] = None,
               url : Optional[str] = None,
               image : Optional[Resourceish] = None,
               images : Optional[list[Resourceish]] = None,
               author_name : Optional[str] = None,
               author_url : Optional[str] = None,
               author_icon : Optional[str] = None,
               color : Optional[str] = None,
               colour : Optional[str] = None,
               ):
    '''
    Parameters
    ----------
    `title` : The title of the post.
    `description` : The description of the post, if it exists.
    `url` : A link to the post.
    `image` : A Resourceish type. Can be a url to an image or a file, or any other resource accepted by Hikari. Ignored if `images` is set.
    `images` : A list of Resourceish objects. Use this for albums and collections linked together from one post.
    `author_name` : The display name of whoever posted the image(s).
    `author_url` : A link to the author's profile.
    `author_icon` : The author's profile image.
    `color`/`colour` : Optional color for the embed. British spelling is ignored if both are set.
    '''
    self.title = title
    self.description = description
    self.url = url
    self.images = images
    self.image = images[0] if images else image
    self.author_name = author_name
    self.author_url = author_url
    self.author_icon = author_icon
    self.colour = color if not colour else color | colour # Defaults to the US spelling if both are set for some reason

  def to_embed(self) -> Embed:
    embed = Embed(title = self.title, description=self.description, url=self.url, colour=self.colour)
    embed.set_author(name=self.author_name, url=self.author_url, icon=self.author_icon)
    embed.set_image(self.image)
    if self.images: embed.add_field(name="Image Count", value=len(self.images))
    return embed
  
  def get_images(self, limit:int = 3) -> list[Resourceish]:
    if len(self.images) >= limit + 1:
      return self.images[1:limit+1]
    else:
      return self.images[1:]