from pygame.transform import flip
import assets
from tiles import Tile
from tiles.default import (
  Floor as DefaultFloor,
  Wall as DefaultWall
)
class Dirt(DefaultFloor):
  sprite = assets.sprites["prejungle_dirt"]

assets.sprites["prejungle_grass_corner_nw"] = assets.sprites["prejungle_grass_corner"]
assets.sprites["prejungle_grass_corner_ne"] = flip(assets.sprites["prejungle_grass_corner"], True, False)
assets.sprites["prejungle_grass_corner_sw"] = flip(assets.sprites["prejungle_grass_corner"], False, True)
assets.sprites["prejungle_grass_corner_se"] = flip(assets.sprites["prejungle_grass_corner"], True, True)

class Grass(DefaultFloor):
  @classmethod
  def render(cls, stage, cell, visited_cells):
    x, y = cell

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Dirt)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Dirt)):
      return assets.sprites["prejungle_grass_corner_nw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Dirt)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Dirt)):
      return assets.sprites["prejungle_grass_corner_ne"]

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Dirt)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Dirt)):
      return assets.sprites["prejungle_grass_corner_sw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Dirt)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Dirt)):
      return assets.sprites["prejungle_grass_corner_se"]

    return assets.sprites["prejungle_grass"]

mappings = {
  ".": Dirt,
  ",": Grass,
}
