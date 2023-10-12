class LadleException(Exception):
  """
  A base exception for ladles to extend.
  """
  def __init__(self, code:str | None = None,
                     message:str | None = None,
                     data:dict | None = None):
    self.code = code
    self.message = message
    self.data = data