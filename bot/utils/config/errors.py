from lightbulb.errors import LightbulbError
class BoxbotException(LightbulbError):
  def __init__(self, message: str, *args):
    self.message = message
    super().__init__(args)

class GuildExistsError(BoxbotException): ...
class GuildNotFoundError(BoxbotException): ...
class UserNotFoundError(BoxbotException): ...