from pygame import Surface
from pygame.transform import flip
import assets
from locations.default.tileset import black_square, OasisStairs
from config import TILE_SIZE
from colors.palette import BLACK


def render_oasis(stage, cell, visited_cells=[]):
  x, y = cell
  o = lambda x, y: (
    stage.is_tile_at_oasis((x, y))
    or stage.is_tile_at_of_type((x, y), OasisStairs)
  )

  if o(x, y - 1) and o(x, y + 1) and not o(x - 1, y):
    return assets.sprites["oasis_edge"]
  elif o(x, y - 1) and o(x, y + 1) and not o(x + 1, y):
    return flip(assets.sprites["oasis_edge"], True, False)
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y - 1):
    return assets.sprites["oasis_edge_top"]
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y + 1):
    return assets.sprites["oasis_edge_bottom"]
  elif o(x + 1, y) and o(x, y + 1) and not o(x - 1, y - 1) and not o(x - 1, y) and not o(x, y - 1):
    return assets.sprites["oasis_corner_top"]
  elif o(x - 1, y) and o(x, y + 1) and not o(x + 1, y - 1) and not o(x + 1, y) and not o(x, y - 1):
    return flip(assets.sprites["oasis_corner_top"], True, False)
  elif o(x + 1, y) and o(x, y - 1) and not o(x - 1, y + 1) and not o(x - 1, y) and not o(x, y + 1):
    return assets.sprites["oasis_corner_bottom"]
  elif o(x - 1, y) and o(x, y - 1) and not o(x + 1, y + 1) and not o(x + 1, y) and not o(x, y + 1):
    return flip(assets.sprites["oasis_corner_bottom"], True, False)

  return black_square
