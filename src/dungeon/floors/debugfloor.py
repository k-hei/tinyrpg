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
          # oasis_room := Room(data=RoomData(**choice(rooms["oasis"]))),
        ]
      ),
      extra_room_count=1,
      seed=seed,
      debug=True
    )
