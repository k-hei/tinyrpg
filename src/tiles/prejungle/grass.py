from pygame.transform import flip, rotate
import assets
from tiles import Tile
from tiles.default import Floor
from tiles.prejungle.dirt import Dirt

assets.sprites["prejungle_grass_edge_w"] = assets.sprites["prejungle_grass_edge"]
assets.sprites["prejungle_grass_edge_e"] = flip(assets.sprites["prejungle_grass_edge"], True, False)
assets.sprites["prejungle_grass_edge_n"] = rotate(assets.sprites["prejungle_grass_edge"], -90)
assets.sprites["prejungle_grass_edge_s"] = rotate(assets.sprites["prejungle_grass_edge"], 90)
assets.sprites["prejungle_grass_corner_nw"] = assets.sprites["prejungle_grass_corner"]
assets.sprites["prejungle_grass_corner_ne"] = flip(assets.sprites["prejungle_grass_corner"], True, False)
assets.sprites["prejungle_grass_corner_sw"] = flip(assets.sprites["prejungle_grass_corner"], False, True)
assets.sprites["prejungle_grass_corner_se"] = flip(assets.sprites["prejungle_grass_corner"], True, True)
assets.sprites["prejungle_grass_incorner_nw"] = assets.sprites["prejungle_grass_incorner"]
assets.sprites["prejungle_grass_incorner_ne"] = flip(assets.sprites["prejungle_grass_incorner"], True, False)
assets.sprites["prejungle_grass_incorner_sw"] = flip(assets.sprites["prejungle_grass_incorner"], False, True)
assets.sprites["prejungle_grass_incorner_se"] = flip(assets.sprites["prejungle_grass_incorner"], True, True)

class Grass(Floor):

  @classmethod
  def render(cls, stage, cell, visited_cells):
    x, y = cell

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x - 1, y - 1)), Dirt)):
      return assets.sprites["prejungle_grass_incorner_nw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y - 1)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x + 1, y - 1)), Dirt)):
      return assets.sprites["prejungle_grass_incorner_ne"]

    if (Tile.is_of_type(stage.get_tile_at((x - 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x - 1, y + 1)), Dirt)):
      return assets.sprites["prejungle_grass_incorner_sw"]

    if (Tile.is_of_type(stage.get_tile_at((x + 1, y)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x, y + 1)), Grass)
    and Tile.is_of_type(stage.get_tile_at((x + 1, y + 1)), Dirt)):
      return assets.sprites["prejungle_grass_incorner_se"]

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

    if Tile.is_of_type(stage.get_tile_at((x - 1, y)), Dirt):
      return assets.sprites["prejungle_grass_edge_w"]

    if Tile.is_of_type(stage.get_tile_at((x, y - 1)), Dirt):
      return assets.sprites["prejungle_grass_edge_n"]

    if Tile.is_of_type(stage.get_tile_at((x + 1, y)), Dirt):
      return assets.sprites["prejungle_grass_edge_e"]

    if Tile.is_of_type(stage.get_tile_at((x, y + 1)), Dirt):
      return assets.sprites["prejungle_grass_edge_s"]

    return assets.sprites["prejungle_grass"]
