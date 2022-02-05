import lightbulb
import re
from typing import Tuple
from . import ladles

def remove_spoilered_text(message:str) -> str:
  '''Quick hacky way to remove spoilers, doesn't handle ||s in code blocks'''
  strs = message.split('||')
  despoilered = ''.join(strs[::2]) # Get every 4th string
  despoilered += strs[-1] if len(strs) % 2 == 0 else ''
  return despoilered

def get_ladles(l_ladles:list[str]) -> list[ladles.Ladle]:
  return [getattr(ladles, name.strip())() for name in l_ladles]

def compile_patterns(l_ladles:list[ladles.Ladle]) -> list[Tuple[ladles.Ladle, re.Pattern]]:
  return [(ladle, re.compile(ladle.pattern)) for ladle in l_ladles]