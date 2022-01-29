from pygame.transform import flip, rotate
import assets
from tiles import Tile
from tiles.default import Oasis, OasisStairs
from tiles.prejungle.grass import Grass

assets.sprites["prejungle_pond_corner_ne"] = flip(assets.sprites["prejungle_pond_corner_nw"], True, False)
assets.sprites["prejungle_pond_corner_se"] = flip(assets.sprites["prejungle_pond_corner_sw"], True, False)
assets.sprites["prejungle_pond_edge_e"] = flip(assets.sprites["prejungle_pond_edge_w"], True, False)

class Pond(Oasis):
  @classmethod
  def render(cls, stage, cell, visited_cells):
    x, y = cell

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Grass)):
      return assets.sprites["prejungle_pond_corner_nw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Grass)):
      return assets.sprites["prejungle_pond_corner_ne"]

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Grass)):
      return assets.sprites["prejungle_pond_corner_sw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Grass)):
      return assets.sprites["prejungle_pond_corner_se"]

    if Tile.is_of_type(stage.get_tile_at((x - 1, y)), Grass):
      return assets.sprites["prejungle_pond_edge_w"]

    if Tile.is_of_type(stage.get_tile_at((x, y - 1)), Grass):
      return assets.sprites["prejungle_pond_edge_n"]

    if Tile.is_of_type(stage.get_tile_at((x + 1, y)), Grass):
      return assets.sprites["prejungle_pond_edge_e"]

    if Tile.is_of_type(stage.get_tile_at((x, y + 1)), Grass):
      return assets.sprites["prejungle_pond_edge_s"]

    return assets.sprites["prejungle_pond"]

class PondStairs(OasisStairs):
  sprite = assets.sprites["prejungle_pond_stairs"]
