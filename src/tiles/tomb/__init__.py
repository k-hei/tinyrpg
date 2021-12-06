import lib.vector as vector
from lib.filters import replace_color
from colors.palette import WHITE, COLOR_TILE

from tiles import Tile
from tiles.tomb.walltop import render_walltop
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
]

for tile_id in TILE_IDS:
  assets.sprites[tile_id] = replace_color(assets.sprites[tile_id], WHITE, COLOR_TILE)

class Floor(Tile):
  sprite = assets.sprites["tomb_floor"]

class Wall(Tile):
  solid = True
  opaque = True
  def sprite(stage, cell, visited_cells=None):
    x, y = cell
    tile_below = stage.get_tile_at((x, y + 1))
    tile_base = stage.get_tile_at((x, y + 2))
    is_elevated = False
    is_special_room = False

    if (
      tile_below in (Floor, Pit, Hallway)
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
  def sprite(stage, cell, visited_cells=None):
    if stage.get_tile_at(vector.add(cell, (0, -1))) is not Pit:
      return assets.sprites["tomb_pit"]
    else:
      return None

class Hallway(Tile):
  sprite = None

class Entrance(Tile):
  sprite = assets.sprites["stairs_up"]

class Exit(Tile):
  sprite = assets.sprites["stairs_down"]

mappings = {
  ".": Floor,
  "#": Wall,
  " ": Pit,
  ",": Hallway,
  "<": Entrance,
  ">": Exit,
}
