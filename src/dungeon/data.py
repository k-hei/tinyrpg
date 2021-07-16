from dataclasses import dataclass
from types import FunctionType
from json import JSONEncoder
from dungeon.stage import Stage, Tile
from dungeon.decor import Decor
from dungeon.element import DungeonElement
from dungeon.features.room import Room

@dataclass
class DungeonData:
  floors: list[Stage]
  floor_index: int
  memory: list[list[tuple[int, int]]]

  class Encoder(JSONEncoder):
    def default(encoder, obj):
      if type(obj) is type and issubclass(obj, Tile):
        return Stage.TILES.index(obj) if obj in Stage.TILES else -1
      if type(obj) in (DungeonData, Stage, Decor):
        return obj.__dict__
      if isinstance(obj, DungeonElement) or isinstance(obj, Room):
        return obj.encode()
      if isinstance(obj, FunctionType):
        return obj.__name__
      return JSONEncoder.default(encoder, obj)
