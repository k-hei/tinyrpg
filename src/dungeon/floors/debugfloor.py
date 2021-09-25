from random import randint
from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.eyeball import Eyeball

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=[
        Room(data=rooms["entry"]),
        Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
          spawns_enemies=True, # [Eyeball(rare=True)],
          spawns_vases=True
        )),
      ],
      # extra_room_count=4 + randint(0, 2),
      seed=seed
    )
