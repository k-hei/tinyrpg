from pygame import Surface
import lib.vector as vector
from lib.filters import replace_color
from colors.palette import BLACK, WHITE, COLOR_TILE

from tiles import Tile
from tiles.tomb.walltop import render_walltop
from tiles.tomb.oasis import render_oasis
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
import assets

TILE_SIZE = 32
TILE_IDS = [
  "tomb_floor",
  "wall_top",
  "wall_bottom",
  "wall_alt",
  "wall_battle",
  "wall_battle_alt",
  "wall_corner",
  "wall_edge",
  "wall_link",
  "stairs_up",
  "stairs_down",
  "oasis_edge",
  "oasis_edge_top",
  "oasis_edge_bottom",
  "oasis_corner_top",
  "oasis_corner_bottom",
  "oasis_stairs_down",
  "oasis_stairs_up",
]
for tile_id in TILE_IDS:
  assets.sprites[tile_id] = replace_color(assets.sprites[tile_id], WHITE, COLOR_TILE)

black_square = Surface((TILE_SIZE, TILE_SIZE))
black_square.fill(BLACK)

class Floor(Tile):
  sprite = assets.sprites["tomb_floor"]

class Wall(Tile):
  solid = True
  opaque = True

  @staticmethod
  def find_state(stage, cell, visited_cells):
    x, y = cell
    return [
      stage.get_tile_at(cell),
      stage.get_tile_at((x - 1, y)),
      stage.get_tile_at((x + 1, y)),
      stage.get_tile_at((x, y - 1)),
      stage.get_tile_at((x, y + 1)),
      (x - 1, y - 1) in visited_cells,
      (    x, y - 1) in visited_cells,
      (x + 1, y - 1) in visited_cells,
      (x - 1,     y) in visited_cells,
      (x + 1,     y) in visited_cells,
      (x - 1, y + 1) in visited_cells,
      (    x, y + 1) in visited_cells,
      (x + 1, y + 1) in visited_cells,
    ]

  def sprite(stage, cell, visited_cells=None):
    x, y = cell
    tile_below = stage.get_tile_at((x, y + 1))
    tile_base = stage.get_tile_at((x, y + 2))
    is_elevated = False
    is_special_room = False

    if (
      tile_below in (Floor, Pit, Hallway, Oasis)
      and (visited_cells is None or (x, y + 1) in visited_cells)
      and not next((e for e in stage.get_elems_at((x, y + 1)) if isinstance(e, Door)), None)
    ):
      if is_special_room:
        if x % (2 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
          return assets.sprites["wall_battle_alt"]
        else:
          return assets.sprites["wall_battle"]
      else:
        if x % (3 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
          return assets.sprites["wall_alt"]
        else:
          return assets.sprites["wall_bottom"]
    elif is_elevated and tile_below is Wall and not (tile_base is None or tile_base is Wall):
      return assets.sprites["wall_top"]
    else:
      return render_walltop(stage, cell, visited_cells)

class Pit(Tile):
  pit = True

  @staticmethod
  def find_state(stage, cell, visited_cells):
    x, y = cell
    return [
      stage.get_tile_at(cell),
      stage.get_tile_at((x, y - 1)),
      (x, y - 1) in visited_cells,
    ]

  def sprite(stage, cell, visited_cells=None):
    if stage.get_tile_at(vector.add(cell, (0, -1))) is not Pit:
      return assets.sprites["tomb_pit"]
    else:
      return black_square

class Hallway(Tile):
  sprite = black_square

class Entrance(Tile):
  sprite = assets.sprites["stairs_up"]

class Escape(Entrance):
  sprite = assets.sprites["stairs_up"]

class Exit(Tile):
  sprite = assets.sprites["stairs_down"]

class Oasis(Tile):
  elev = -1.0

  def sprite(stage, cell, visited_cells):
    return render_oasis(stage, cell, visited_cells)

class OasisStairs(Tile):
  elev = -0.5

  def sprite(stage, cell, _):
    x, y = cell
    if issubclass(stage.get_tile_at((x, y - 1)), Floor):
      return assets.sprites["oasis_stairs_down"]
    else:
      return assets.sprites["oasis_stairs_up"]

mappings = {
  ".": Floor,
  "#": Wall,
  " ": Pit,
  ",": Hallway,
  "<": Entrance,
  ">": Exit,
  "E": Escape,
  "O": Oasis,
  "I": OasisStairs,
}
