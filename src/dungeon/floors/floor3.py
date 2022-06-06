from random import random, randint
from lib.graph import Graph
from lib.cell import neighborhood
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.props.pillar import Pillar
import locations.tomb.tiles as tileset

class Floor3(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: Graph(
        nodes=[
          mageboss_room := Room(data=rooms["mageboss"]),
          emerald_room := Room(data=rooms["emerald"]),
          hall_room := Room(data=rooms["hall"]),
          entry_room := Room(cells=gen_blob(min_area=60), data=RoomData(
            secret=True,
            terrain=False,
            hooks={
              "on_place": lambda room, stage: (
                setattr(stage, "entrance", next((c for c in sorted(room.cells, key=lambda c: random()) if (
                  not next((n for n in neighborhood(c, diagonals=True) if issubclass(stage.get_tile_at(n), tileset.Wall)), None)
                )), room.center)),
                stage.set_tile_at(stage.entrance, tileset.Entrance),
                pillar_cells := [c for c in room.cells if (
                  issubclass(stage.get_tile_at(c), tileset.Floor)
                  and not next((n for n in neighborhood(c) if issubclass(stage.get_tile_at(n), tileset.Wall) or n == stage.entrance), None)
                  and len([n for n in neighborhood(c, diagonals=True) if issubclass(stage.get_tile_at(n), tileset.Wall)]) == 1
                )],
                [stage.spawn_elem_at(c, Pillar()) for c in sorted(pillar_cells, key=lambda c: random()) if (
                  randint(0, 1)
                  and not next((n for n in neighborhood(c, diagonals=True) if (
                    next((e for e in stage.get_elems_at(n) if isinstance(e, Pillar)), None)
                  )), None)
                )]
              )
            }
          )),
        ],
        edges=[
          (emerald_room, mageboss_room),
          (mageboss_room, hall_room),
          (hall_room, entry_room),
        ]
      ),
      seed=seed
    )
