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


class GiantFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=lambda: [
        Room(cells=gen_blob(min_area=400), data=RoomData(
          items=[choice(SPECIAL_ITEMS) for i in range(randint(3, 5))],
          enemies=True,
          hooks={
            "on_place": lambda room, stage: (
              valid_cells := [c for c in room.cells
                if stage.is_cell_empty(c)
                and not stage.is_tile_at_pit(c)],
              valid_cells and (
                entrance := choice(valid_cells),
                entrance and (
                  stage.set_tile_at(entrance, stage.tileset.Entrance),
                  valid_cells.remove(entrance),
                ),
              ),
              valid_cells and (
                exit := choice(valid_cells),
                exit and (
                  stage.set_tile_at(exit, stage.tileset.Exit),
                  valid_cells.remove(exit),
                ),
              ),
            )
          }
        )),
      ],
      items=SPECIAL_ITEMS,
      enemies=[Eyeball, Eyeball, Eyeball, Mushroom, Mushroom, Ghost, Mummy, Snake, Cactus],
      seed=seed
    )
