from lib.graph import Graph
from contexts.explore.roomdata import rooms
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.gen import gen_floor


class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          Room(data=rooms["entry"]),
          puzzle_room := Room(data=rooms["pzlt1"]),
          key_room := Room(data=rooms["key"]),
        ],
        edges=[
          (puzzle_room, key_room),
        ]
      ),
      extra_room_count=1,
      seed=seed,
      debug=True
    )
