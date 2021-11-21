from pygame import Surface, SRCALPHA
from pygame.transform import rotate, flip
import assets
from dungeon.props.secretdoor import SecretDoor
from colors.palette import BLACK
from config import TILE_SIZE

def render_walltop(stage, cell, visited_cells=None):
  x, y = cell
  Wall = stage.get_tile_at(cell)
  is_wall = lambda x, y: (
    (visited_cells is not None and (x, y) not in visited_cells)
    or stage.get_tile_at((x, y)) is None
    or (stage.get_tile_at((x, y)) is Wall or SecretDoor.exists_at(stage, (x, y))) and (
      (visited_cells is not None and (x, y + 1) not in visited_cells)
      or stage.get_tile_at((x, y + 1)) is None
      or stage.get_tile_at((x, y + 1)) is Wall
      or next((e for e in stage.get_elems_at((x, y + 1))), None)
    )
  )

  surface = Surface((TILE_SIZE, TILE_SIZE), SRCALPHA)
  surface.fill(BLACK)

  edge = assets.sprites["wall_edge"]
  if "wall_edge_left" not in assets.sprites:
    assets.sprites["wall_edge_left"] = edge
  edge_left = assets.sprites["wall_edge_left"]

  if "wall_edge_bottom" not in assets.sprites:
    assets.sprites["wall_edge_bottom"] = rotate(edge, 90)
  edge_bottom = assets.sprites["wall_edge_bottom"]

  if "wall_edge_right" not in assets.sprites:
    assets.sprites["wall_edge_right"] = rotate(edge, 180)
  edge_right = assets.sprites["wall_edge_right"]

  if "wall_edge_top" not in assets.sprites:
    assets.sprites["wall_edge_top"] = rotate(edge, 270)
  edge_top = assets.sprites["wall_edge_top"]

  corner = assets.sprites["wall_corner"]

  if "wall_corner_nw" not in assets.sprites:
    assets.sprites["wall_corner_nw"] = corner
  corner_nw = assets.sprites["wall_corner_nw"]

  if "wall_corner_sw" not in assets.sprites:
    assets.sprites["wall_corner_sw"] = rotate(corner, 90)
  corner_sw = assets.sprites["wall_corner_sw"]

  if "wall_corner_se" not in assets.sprites:
    assets.sprites["wall_corner_se"] = rotate(corner, 180)
  corner_se = assets.sprites["wall_corner_se"]

  if "wall_corner_ne" not in assets.sprites:
    assets.sprites["wall_corner_ne"] = rotate(corner, 270)
  corner_ne = assets.sprites["wall_corner_ne"]

  link = assets.sprites["wall_link"]

  if not is_wall(x - 1, y):
    surface.blit(edge_left, (0, 0))
    if is_wall(x, y - 1):
      surface.blit(link, (0, 0))
    if is_wall(x, y + 1):
      surface.blit(flip(link, False, True), (0, 0))

  if not is_wall(x + 1, y):
    surface.blit(edge_right, (0, 0))
    if is_wall(x, y - 1):
      surface.blit(flip(link, True, False), (0, 0))
    if is_wall(x, y + 1):
      surface.blit(flip(link, True, True), (0, 0))

  if not is_wall(x, y - 1):
    surface.blit(edge_top, (0, 0))

  if not is_wall(x, y + 1):
    surface.blit(edge_bottom, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y - 1) and not is_wall(x - 1, y - 1)
  or not is_wall(x - 1, y) and not is_wall(x, y - 1)):
    surface.blit(corner_nw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y - 1) and not is_wall(x + 1, y - 1)
  or not is_wall(x + 1, y) and not is_wall(x, y - 1)):
    surface.blit(corner_ne, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y + 1) and not is_wall(x - 1, y + 1)
  or not is_wall(x - 1, y) and not is_wall(x, y + 1)):
    surface.blit(corner_sw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y + 1) and not is_wall(x + 1, y + 1)
  or not is_wall(x + 1, y) and not is_wall(x, y + 1)):
    surface.blit(corner_se, (0, 0))

  if not is_wall(x, y - 1) and is_wall(x - 1, y):
    surface.blit(rotate(flip(link, False, True), -90), (0, 0))

  if not is_wall(x, y - 1) and is_wall(x + 1, y):
    surface.blit(rotate(link, -90), (0, 0))

  if is_wall(x - 1, y) and not is_wall(x, y + 1):
    surface.blit(rotate(link, 90), (0, 0))

  if is_wall(x + 1, y) and not is_wall(x, y + 1):
    surface.blit(rotate(flip(link, True, False), -90), (0, 0))

  return surface
