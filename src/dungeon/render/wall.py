from pygame import Surface, SRCALPHA
from pygame.transform import rotate, flip
import assets
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
from colors.palette import BLACK
from config import TILE_SIZE

def render_wall(stage, cell, visited_cells=[]):
  x, y = cell
  def is_wall(x, y):
    door = stage.get_elem_at((x, y), superclass=Door)
    return (
      (x, y) not in visited_cells
      or stage.get_tile_at((x, y)) is None
      or stage.get_tile_at((x, y)) is stage.WALL and (
        (x, y + 1) not in visited_cells
        or stage.get_tile_at((x, y + 1)) is None
        or stage.get_tile_at((x, y + 1)) is stage.WALL
        or stage.get_elem_at((x, y + 1), superclass=Door)
      )
      or next((e for e in stage.get_elems_at((x, y)) if type(e) is SecretDoor and e.hidden), None)
      or stage.get_tile_at((x, y)) is stage.DOOR_WAY and (
        next((e for e in stage.get_elems_at((x, y - 1)) if type(e) is SecretDoor and e.hidden), None)
        or next((e for e in stage.get_elems_at((x, y + 1)) if type(e) is SecretDoor and e.hidden), None)
      )
    )
  is_door = lambda x, y: stage.get_elem_at((x, y), superclass=Door)

  sprite = Surface((TILE_SIZE, TILE_SIZE), SRCALPHA)
  sprite.fill(BLACK)

  edge_left = assets.sprites["wall_edge"]
  if "wall_edge_bottom" not in assets.sprites:
    assets.sprites["wall_edge_bottom"] = rotate(edge_left, 90)
  edge_bottom = assets.sprites["wall_edge_bottom"]
  if "wall_edge_right" not in assets.sprites:
    assets.sprites["wall_edge_right"] = rotate(edge_left, 180)
  edge_top = assets.sprites["wall_edge_right"]
  if "wall_edge_top" not in assets.sprites:
    assets.sprites["wall_edge_top"] = rotate(edge_left, 270)
  edge_top = assets.sprites["wall_edge_top"]

  corner_nw = assets.sprites["wall_corner"]
  if "wall_corner_sw" not in assets.sprites:
    assets.sprites["wall_corner_sw"] = rotate(corner_nw, 90)
  corner_sw = assets.sprites["wall_corner_sw"]
  if "wall_corner_se" not in assets.sprites:
    assets.sprites["wall_corner_se"] = rotate(corner_nw, 180)
  corner_se = assets.sprites["wall_corner_se"]
  if "wall_corner_ne" not in assets.sprites:
    assets.sprites["wall_corner_ne"] = rotate(corner_nw, 270)
  corner_ne = assets.sprites["wall_corner_ne"]

  edge_right = rotate(edge_left, 180)
  link = assets.sprites["wall_link"]

  if not is_wall(x - 1, y):
    sprite.blit(edge_left, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(link, (0, 0))
    if is_wall(x, y + 1):
      sprite.blit(flip(link, False, True), (0, 0))

  if not is_wall(x + 1, y):
    sprite.blit(edge_right, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(flip(link, True, False), (0, 0))
    if is_wall(x, y + 1):
      sprite.blit(flip(link, True, True), (0, 0))

  if not is_wall(x, y - 1):
    sprite.blit(edge_top, (0, 0))

  if not is_wall(x, y + 1):
    sprite.blit(edge_bottom, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y - 1) and not is_wall(x - 1, y - 1)
  or not is_wall(x - 1, y) and not is_wall(x, y - 1)):
    sprite.blit(corner_nw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y - 1) and not is_wall(x + 1, y - 1)
  or not is_wall(x + 1, y) and not is_wall(x, y - 1)):
    sprite.blit(corner_ne, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y + 1) and not is_wall(x - 1, y + 1)
  or not is_wall(x - 1, y) and not is_wall(x, y + 1)):
    sprite.blit(corner_sw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y + 1) and not is_wall(x + 1, y + 1)
  or not is_wall(x + 1, y) and not is_wall(x, y + 1)):
    sprite.blit(corner_se, (0, 0))

  if not is_wall(x, y - 1) and is_wall(x - 1, y):
    sprite.blit(rotate(flip(link, False, True), -90), (0, 0))

  if not is_wall(x, y - 1) and is_wall(x + 1, y):
    sprite.blit(rotate(link, -90), (0, 0))

  if is_wall(x - 1, y) and not is_wall(x, y + 1):
    sprite.blit(rotate(link, 90), (0, 0))

  if is_wall(x + 1, y) and not is_wall(x, y + 1):
    sprite.blit(rotate(flip(link, True, False), -90), (0, 0))

  return sprite
