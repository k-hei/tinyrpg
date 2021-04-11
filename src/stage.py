from dataclasses import dataclass

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
  STAIRS = Tile(solid=False, opaque=False)

  def __init__(stage, size):
    (width, height) = size
    stage.size = size
    stage.data = [Stage.FLOOR] * (width * height)
    stage.actors = []

  def fill(stage, data):
    (width, height) = stage.size
    for i in range(width * height):
      stage.data[i] = data

  def get_cells(stage):
    (width, height) = stage.size
    cells = []
    for y in range(height):
      for x in range(width):
        cells.append((x, y))
    return cells

  def get_actor_at(stage, cell):
    for actor in stage.actors:
      if actor.cell[0] == cell[0] and actor.cell[1] == cell[1]:
        return actor
    return None

  def get_tile_at(stage, cell):
    if not stage.contains(cell):
      return None
    width = stage.size[0]
    (x, y) = cell
    return stage.data[y * width + x]

  def set_tile_at(stage, cell, data):
    if not stage.contains(cell):
      return
    width = stage.size[0]
    (x, y) = cell
    stage.data[y * width + x] = data

  def spawn(stage, actor, cell=None):
    stage.actors.append(actor)
    if cell:
      actor.cell = cell

  def kill(stage, actor):
    stage.actors.remove(actor)

  def contains(stage, cell):
    (width, height) = stage.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height
