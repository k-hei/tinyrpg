from pygame import Surface
from pygame.transform import flip
import assets
import tiles.default as tileset
from config import TILE_SIZE
from colors.palette import BLACK

black_square = Surface((TILE_SIZE, TILE_SIZE))
black_square.fill(BLACK)

def render_oasis(stage, cell, visited_cells=[]):
  x, y = cell
  o = lambda x, y: (
    issubclass(stage.get_tile_at((x, y)), tileset.Oasis)
    or issubclass(stage.get_tile_at((x, y)), tileset.OasisStairs)
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
