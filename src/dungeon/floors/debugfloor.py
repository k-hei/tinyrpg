from random import choice
from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import RoomData, rooms
from dungeon.gen import gen_floor

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: Graph(
        nodes=[
          Room(data=RoomData(**rooms["entry"])),
          # Room(data=RoomData(**choice(rooms["oasis"]))),
          Room(data=RoomData(**rooms["pzlt1"])),
        ]
      ),
      extra_room_count=1,
      seed=seed
    )
