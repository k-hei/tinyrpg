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
      features=Graph(
        nodes=[
          entry_room := Room(data=RoomData(**rooms["entry"])),
          exit_room := Room(data=RoomData(**rooms["exit"], doors="RareTreasureDoor")),
          puzzle_room := Room(data=RoomData(**rooms["pzlt1"])),
          buffer_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_vases=True,
            degree=2
          )),
          intro_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(), Eyeball()],
            degree=3
          )),
          key_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_vases=True,
            degree=1
          )),
          Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(rare=True), Mushroom(), Mushroom()],
            spawns_vases=True,
            degree=1,
            secret=True
          )),
        ],
        edges=[
          (entry_room, buffer_room),
          (buffer_room, intro_room),
          (intro_room, exit_room),
          (puzzle_room, key_room),
        ]
      ),
      extra_room_count=4, # 4 + randint(0, 2),
      seed=seed
    )
