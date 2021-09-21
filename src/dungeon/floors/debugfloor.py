from lib.graph import Graph
import assets
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          mageboss_room := Room(data=assets.rooms["mageboss"]),
          emerald_room := Room(data=assets.rooms["emerald"]),
          buffer_room := Room(cells=gen_blob(min_area=60, max_area=100), data=RoomData(spawns_vases=True)),
          # treasure_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(spawns_vases=True, doors="TreasureDoor", degree=1)),
          # arena_room := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True)),
          enemy_room1 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True)),
          # enemy_room2 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True)),
          # enemy_room3 := Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_enemies=True)),
          # Room(cells=gen_blob(min_area=120, max_area=160), data=RoomData(spawns_vases=True, spawns_enemies=True)),
          entry_room := Room(data=assets.rooms["entry"]),
          oasis_room := Room(data=assets.rooms["oasis"]),
        ],
        edges=[
          (mageboss_room, emerald_room),
          (mageboss_room, buffer_room),
          (entry_room, oasis_room),
          (enemy_room1, entry_room),
          # (arena_room, treasure_room),
          # (enemy_room1, enemy_room2),
          # (entry_room, buffer_room),
          # (enemy_room2, enemy_room3),
          # (enemy_room3, enemy_room1),
        ]
      ),
      seed=seed
    )
