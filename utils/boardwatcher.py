import json
import re
from logging import getLogger
from typing import Tuple
from aiohttp import ClientError

from utils.fourchanaio import Chan, Post

logger = getLogger("boardwatcher")

class BoardWatcher:
  def __init__(self, search_patterns:str, regex:str, chan:Chan):
    self._chan = chan
    self._last_modified_time = 0
    
    self._search_patterns = search_patterns
    self._regex = regex

    self._patterns = {}
    self._exclude_patterns = {}
    self._boards = set()
    self._tracked_threads = self.loadTrackedThreads()
    
    self.load_patterns(self._search_patterns)

  async def update(self) -> list[Post]:
    '''Refresh the internal database and return a list of new threads'''
    newThreads = list[Post]
    # Clean threadlist, then update boards
    await self.cleanup_untracked_boards()
    for board in self._boards:
      newMatchedThreads = await self.update_board(board)
      newThreads.extend(newMatchedThreads)
    self.saveTrackedThreads()
    return newThreads

  async def update_board(self, board:str) -> list[Post]:
    logger.debug(f"checking for new threads on {board}")

    # Get new threads from 4chan
    liveThreads:list[Post] = await self.fetch_threads(board)
    self.cleanup_board(board, liveThreads)
    
    newThreads = []
    filtered = [i for i in liveThreads 
                if 			any(map(lambda x: x.search(i.comment) or x.search(i.subject), self._patterns.get(board, [])))
                and not any(map(lambda x: x.search(i.comment) or x.search(i.subject), self._exclude_patterns.get(board, [])))]
    
    # Add new threads only if they are not being tracked
    for thread in filtered:
      if thread.no not in self._tracked_threads[board]:
        newThreads.append(thread)
        logger.info(f"Started tracking {thread.url}")
        self._tracked_threads[board][thread.no] = thread
    return newThreads

  def cleanup_board(self, board:str, threads:list[Post]) -> None:
    '''Remove dead threads in tracked boards'''
    threadNos = [t.no for t in threads]
    for no in list(self._tracked_threads.setdefault(board, {})):
      if not no in threadNos:
        t = self._tracked_threads[board].pop(no)
        logger.info(f"Stopped tracking {t.url}")
  
  async def cleanup_untracked_boards(self) -> None:
    '''Remove threads belonging to untracked boards'''
    untrackedBoards = [b for b in self._tracked_threads if b not in self._boards]
    for board in untrackedBoards:
      for no in self._tracked_threads[board]:
        thread = self._tracked_threads[board][no]
        logger.info(f"Stopped tracking {thread.url}")
      self._tracked_threads.pop(board, None)
      self._patterns.pop(board, None)
      self._exclude_patterns.pop(board, None)

  def load_patterns(self, input:str):
    self._boards = set()	# Clear the bag of boards
    self._patterns = {}
    self._exclude_patterns = {}

    search_patterns = input.split("&&")
    for entry in search_patterns:
      # Match options using a regex
      match = re.match(self._regex, entry)
      try: 
        flags, exclude = self.parse_args(match.group("flags")) # Parse arguments
        patterns = self.parse_patterns(match.group("search_patterns"), flags) # Get a list of patterns with regex options
      except re.error as e:
        logger.warning(f"couldn't compile \"{entry.rstrip()}\": {e}")
      except AttributeError as e:
        logger.critical(f"Line \"{entry.rstrip()}\" resulted in a NoneType:\n{e}")
      else:
        boards = self.parse_boards(match.group("boards"))
        if exclude:
          for board in boards:
            self._boards.add(board)
            for p in patterns:
              self._exclude_patterns.setdefault(board, []).append(p)
        else:
          for board in boards:
            self._boards.add(board)
            for p in patterns:
              self._patterns.setdefault(board, []).append(p)

  #==============================#
  #				Getters/Setters				 #
  #==============================#

  def getTrackedThreads(self):
    threads = []
    for board in self._tracked_threads:
      for threadNo in self._tracked_threads[board]:
        threads.append((self._tracked_threads[board][threadNo]))
    return threads

  def setTrackedThreads(self, newDict = {}):
    self._tracked_threads = newDict
  
  def printTrackedThreads(self):
    for board in self._boards:
      for thread in self._tracked_threads[board]:
        print(self._tracked_threads[board][thread].url)

  def saveTrackedThreads(self) -> None:
    tracked_threads = {board: {
      post_id: (post._data, post.board) for post_id, post in self._tracked_threads[board].items()
    } for board in self._tracked_threads}
    with open("./.cache/tracked_threads.json", "w") as file:
      json.dump(tracked_threads, file)

  def loadTrackedThreads(self) -> dict[str, dict[int, Post]]:
    try:
      tracked_threads = None
      with open("./.cache/tracked_threads.json", "r") as file:
        tracked_threads = json.load(file)
      return {board: {
        # json only supports strings as keys, so post_id must be converted back to an int
        int(post_id): Post(*post) for post_id, post in tracked_threads[board].items()
      } for board in tracked_threads}
    except (FileNotFoundError, AttributeError) as e:
      logger.warning("Could not open tracked threads file!")
    except ValueError as ve:
      pass
    return {}
  
  

  #==============================#
  #				 Private methods			 #
  #==============================#

  async def fetch_threads(self, board) -> list[Post]:
    '''Retrieve threads from a specified 4chan board'''
    try:	# Get threads from 4chan
      threads = await self._chan.catalog(board)
      return threads
    except ClientError:
      logger.warning("Failed to update threads due to a network error")
      return []

  def parse_patterns(self, argString, flags) -> list[re.Pattern]:
    '''Parse comma-separated arguments into a list and return regex patterns'''
    patterns = [x.strip() for x in argString.split(",") if len(x.strip()) > 0]
    return [re.compile(x, flags) for x in patterns] # Compile patterns

  def parse_args(self, argstr:str) -> Tuple[int, bool]:
    '''Parse a string of arguments and return the respective flags'''
    # Split arguments into an array, strip whitespace, and remove null values all at once!
    # List comprehension is wonderful!
    args = [x.strip() for x in argstr.split(",")]
    regex_flags = 0
    exclude = False
    for a in args:
      if a == "i":
        regex_flags |= re.IGNORECASE
      elif a == "e":
        exclude = True
    return regex_flags, exclude

  def parse_boards(self, boards:str):
    '''Parse boards and add to an array'''
    return [x.strip() for x in boards.split(",")]
  
  async def close(self) -> None:
    await self._chan.close()
