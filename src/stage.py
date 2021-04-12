from dataclasses import dataclass
from assets import load as load_assets
import config

@dataclass
class Tile:
  solid: bool
  opaque: bool

class Stage:
  FLOOR = Tile(solid=False, opaque=False)
  WALL = Tile(solid=True, opaque=True)
  DOOR = Tile(solid=True, opaque=True)
  DOOR_OPEN = Tile(solid=False, opaque=False)
  DOOR_HIDDEN = Tile(solid=True, opaque=True)
  STAIRS_UP = Tile(solid=False, opaque=False)
  STAIRS_DOWN = Tile(solid=False, opaque=False)

  def __init__(stage, size):
    (width, height) = size
    stage.size = size
    stage.data = [Stage.FLOOR] * (width * height)
    stage.actors = []
    stage.rooms = []

  def fill(stage, data):
    (width, height) = stage.size
    for i in range(width * height):
      stage.data[i] = data

  def get_cells(stage):
    width, height = stage.size
    cells = []
    for y in range(height):
      for x in range(width):
        cells.append((x, y))
    return cells

  def get_actor_at(stage, cell):
    return next((actor for actor in stage.actors if actor.cell == cell), None)

  def get_tile_at(stage, cell):
    if not stage.contains(cell):
      return None
    width = stage.size[0]
    x, y = cell
    return stage.data[y * width + x]

  def set_tile_at(stage, cell, data):
    if not stage.contains(cell):
      return
    width = stage.size[0]
    x, y = cell
    stage.data[y * width + x] = data

  def find_tile(stage, tile):
    width, height = stage.size
    for y in range(height):
      for x in range(width):
        cell = (x, y)
        if stage.get_tile_at(cell) is tile:
          return cell
    return None

  def spawn_actor(stage, actor, cell=None):
    stage.actors.append(actor)
    if cell:
      actor.cell = cell

  def remove_actor(stage, actor):
    if actor in stage.actors:
      stage.actors.remove(actor)
      actor.cell = None

  def contains(stage, cell):
    (width, height) = stage.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height

  def render_tiles(stage, surface, visible_cells=None, visited_cells=[], camera_pos=None):
    camera_x, camera_y = (0, 0)
    if camera_pos:
      camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    for cell in visible_cells:
      col, row = cell
      sprite = stage.render_tile(cell)
      if sprite:
        opacity = 255
        if cell not in visible_cells:
          opacity = 127
        sprite.set_alpha(opacity)
        x = col * config.tile_size - round(camera_x)
        y = row * config.tile_size - round(camera_y)
        surface.blit(sprite, (x, y))
        sprite.set_alpha(None)

  def render_tile(stage, cell):
    assets = load_assets()
    x, y = cell
    sprite_name = None
    tile = stage.get_tile_at(cell)
    if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
      if stage.get_tile_at((x, y + 1)) is Stage.FLOOR:
        sprite_name = "wall_base"
      else:
        sprite_name = "wall"
    elif tile is Stage.STAIRS_UP:
      sprite_name = "stairs_up"
    elif tile is Stage.STAIRS_DOWN:
      sprite_name = "stairs_down"
    elif tile is Stage.DOOR:
      sprite_name = "door"
    elif tile is Stage.DOOR_OPEN:
      sprite_name = "door_open"
    elif tile is Stage.FLOOR:
      sprite_name = "floor"
    if sprite_name is not None:
      return assets.sprites[sprite_name]
    else:
      return None
