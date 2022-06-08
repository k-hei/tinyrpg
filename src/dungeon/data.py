from dataclasses import dataclass, field
from types import FunctionType
from json import JSONEncoder
from cores import Core
from dungeon.stage import Stage, Tile
from dungeon.decor import Decor
from dungeon.element import DungeonElement

@dataclass
class DungeonData:
  floors: list[Stage]
  floor_index: int = 0
  memory: list[list[tuple[int, int]]] = field(default_factory=lambda: [])

  class Encoder(JSONEncoder):
    def default(encoder, obj):
      if type(obj) is type and issubclass(obj, Tile):
        return Stage.TILES.index(obj) if obj in Stage.TILES else -1
      if type(obj) in (DungeonData, Stage, Decor):
        return obj.__dict__
      if isinstance(obj, DungeonElement):
        return obj.encode()
      if isinstance(obj, FunctionType):
        return obj.__name__
      if isinstance(obj, Core):
        return None
      return JSONEncoder.default(encoder, obj)
