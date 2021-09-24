from lib.graph import Graph
import assets
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob

class Floor4(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          mageboss_room := Room(data=assets.rooms["mageboss"]),
          emerald_room := Room(data=assets.rooms["emerald"]),
          buffer_room := Room(cells=gen_blob(min_area=60, max_area=100), data=RoomData(spawns_vases=True, degree=3)),
          oasis_room := Room(data=assets.rooms["oasis"]),
          entry_room := Room(data=assets.rooms["entry"]),
          enemy_room1 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True, spawns_vases=True, degree=3, hooks={ "on_place": "arena.place", "on_defeat": "arena.defeat" })),
          enemy_room2 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True, spawns_vases=True, degree=3, hooks={ "on_place": "arena.place", "on_defeat": "arena.defeat" })),
          enemy_room3 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True, spawns_vases=True, degree=3, hooks={ "on_place": "arena.place", "on_defeat": "arena.defeat" })),
          treasure_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(spawns_vases=True, doors="TreasureDoor", degree=1)),
        ],
        edges=[
          (mageboss_room, emerald_room),
          (mageboss_room, buffer_room),
          (enemy_room1, enemy_room2),
          (enemy_room2, enemy_room3),
          (enemy_room3, enemy_room1),
          (enemy_room1, entry_room),
          (enemy_room2, treasure_room),
        ]
      ),
      seed=seed
    )
