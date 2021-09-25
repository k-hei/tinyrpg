from random import randint
from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=[
        Room(data=rooms["entry"]),
        Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
          spawns_enemies=[Eyeball(rare=True), Mushroom(), Mushroom()],
          spawns_vases=True
        )),
      ],
      # extra_room_count=4 + randint(0, 2),
      seed=seed
    )
