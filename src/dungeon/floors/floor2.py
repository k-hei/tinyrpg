from random import randint, choice
from lib.graph import Graph
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy
from dungeon.actors.skeleton import Skeleton

from items.sets import SPECIAL_ITEMS

class Floor2(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          entry_room := Room(data=rooms["entry2f"]),
          coffin_room := Room(data=rooms["coffin"]),
          enemy_room1 := Room(cells=gen_blob(min_area=80), data=RoomData(enemies=True)),
          enemy_room2 := Room(cells=gen_blob(min_area=80), data=RoomData(enemies=True)),
          enemy_room3 := Room(cells=gen_blob(min_area=80), data=RoomData(enemies=True)),
          enemy_room4 := Room(cells=gen_blob(min_area=120), data=RoomData(enemies=True, items=True, degree=3)),
          exit_room := Room(data=RoomData(**{
            **rooms["exit"].__dict__,
            "edges": [
              [2, 5]
            ]
          })),
          arena_room := Room(data=rooms["arena"]),
          buffer_room := Room(cells=gen_blob(min_area=60), data=RoomData(
            degree=2,
            items=True
          )),
          Room(data=choice(rooms["oasis"])),
          Room(cells=gen_blob(min_area=60), data=RoomData(
            terrain=False,
            degree=1,
            items=[choice(SPECIAL_ITEMS) for i in range(randint(3, 5))],
            doors="TreasureDoor"
          )),
          Room(cells=gen_blob(min_area=60), data=RoomData(
            terrain=False,
            degree=1,
            items=[choice(SPECIAL_ITEMS) for i in range(randint(3, 5))],
            enemies=[Skeleton(rare=True), Mummy(), Mummy()],
            secret=True
          ))
        ],
        edges=[
          (entry_room, coffin_room),
          (coffin_room, enemy_room1),
          (coffin_room, enemy_room2),
          (coffin_room, enemy_room3),
          (enemy_room2, enemy_room4),
          (enemy_room4, enemy_room3),
          (exit_room, arena_room),
          (arena_room, buffer_room),
          (buffer_room, enemy_room4),
        ]
      ),
      # extra_room_count=5, # 4 + randint(0, 2),
      enemies=[Eyeball, Eyeball, Eyeball, Eyeball, Mushroom, Mushroom, Ghost, Mummy],
      seed=seed,
      debug=True
    )
