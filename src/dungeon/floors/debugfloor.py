from random import randint, choice
from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.mummy import Mummy

from items.sets import SPECIAL_ITEMS

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          entry_room := Room(data=RoomData(**rooms["entry"])),
          arena_room := Room(data=RoomData(**rooms["mageboss"])),
        ],
        edges=[
          (entry_room, arena_room),
        ]
      ),
      # extra_room_count=5, # 4 + randint(0, 2),
      seed=seed,
      debug=True
    )
