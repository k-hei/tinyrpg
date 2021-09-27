from random import randint, choice
from lib.graph import Graph
import assets
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from items.sets import SPECIAL_ITEMS

class GenericFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: [
        Room(data=RoomData(**rooms["entry"])),
        Room(data=RoomData(**rooms["exit"])),
        *([Room(data=RoomData(**choice(rooms["oasis"])))] if randint(1, 3) == 1 else []),
        *([Room(cells=gen_blob(min_area=60), data=RoomData(
          terrain=False,
          degree=1,
          items=[choice(SPECIAL_ITEMS) for i in range(randint(3, 5))],
          doors="TreasureDoor"
        ))] if randint(1, 3) == 1 else []),
      ],
      extra_room_count=4 + randint(0, 1),
      items=SPECIAL_ITEMS,
      seed=seed
    )
