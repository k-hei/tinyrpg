from random import randint, choice
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy
from locations.desert.elems.snake import DesertSnake as Snake
from locations.desert.elems.cactus import DesertEvilCactus as Cactus
from items.sets import SPECIAL_ITEMS

class GenericFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: [
        Room(data=rooms["entry"]),
        Room(data=rooms["exit"]),
        *([Room(data=choice(rooms["oasis"]))] if randint(1, 3) == 1 else []),
        *([Room(cells=gen_blob(min_area=60), data=RoomData(
          terrain=False,
          degree=1,
          items=[choice(SPECIAL_ITEMS) for i in range(randint(3, 5))],
          doors="TreasureDoor"
        ))] if randint(1, 3) == 1 else []),
      ],
      extra_room_count=4 + randint(0, 1),
      items=SPECIAL_ITEMS,
      enemies=[Eyeball, Eyeball, Eyeball, Mushroom, Mushroom, Ghost, Mummy, Snake, Cactus],
      seed=seed
    )
