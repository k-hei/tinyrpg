from random import randint
from lib.graph import Graph
import assets
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=[
        Room(data=assets.rooms["entry"]),
        Room(data=assets.rooms["exit"]),
        *([Room(data=assets.rooms["oasis"])] if randint(1, 3) == 1 else []),
      ],
      extra_room_count=4 + randint(0, 1),
      seed=seed
    )
