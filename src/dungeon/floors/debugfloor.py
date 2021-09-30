from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData, rooms
from dungeon.gen import gen_floor

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: Graph(
        nodes=[
          entry_room := Room(data=RoomData(**rooms["entry1f"])),
          puzzle_room := Room(data=RoomData(**rooms["pzlt1"]))
        ]
      ),
      seed=seed
    )
