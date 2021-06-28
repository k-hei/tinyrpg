from dataclasses import dataclass
from dungeon.props.door import Door

@dataclass
class Tile:
  solid: bool
  opaque: bool = False
  elev: float = 0.0

class Stage:
  FLOOR = Tile(solid=False, opaque=False)
  WALL = Tile(solid=True, opaque=True)
  FLOOR_ELEV = Tile(solid=False, opaque=False, elev=1.0)
  WALL_ELEV = Tile(solid=True, opaque=False)
  STAIRS = Tile(solid=False, opaque=False, elev=0.5)
  LADDER = Tile(solid=False, opaque=False, elev=0.5)
  PIT = Tile(solid=True, opaque=False)
  DOOR = Tile(solid=True, opaque=True)
  DOOR_OPEN = Tile(solid=False, opaque=False)
  DOOR_HIDDEN = Tile(solid=True, opaque=True)
  DOOR_LOCKED = Tile(solid=True, opaque=True)
  DOOR_WAY = Tile(solid=False, opaque=False)
  STAIRS_UP = Tile(solid=False, opaque=False)
  STAIRS_DOWN = Tile(solid=False, opaque=False)
  MONSTER_DEN = Tile(solid=False, opaque=False)
  COFFIN = Tile(solid=True, opaque=True)
  OASIS = Tile(solid=False, opaque=False, elev=-1.0)
  OASIS_STAIRS = Tile(solid=False, opaque=False, elev=-0.5)
  TILES = [FLOOR, WALL, STAIRS_DOWN, STAIRS_UP, PIT, DOOR_WAY]

  def __init__(stage, size, data=None, elems=None):
    width, height = size
    stage.size = size
    stage.data = data or [Stage.FLOOR] * (width * height)
    stage.elems = elems or []
    stage.rooms = []
    stage.decors = []
    stage.entrance = None
    stage.stairs = None
    stage.trap_sprung = False

  def fill(stage, data):
    width, height = stage.size
    for i in range(width * height):
      stage.data[i] = data

  def get_width(stage):
    width, _ = stage.size
    return width

  def get_height(stage):
    _, height = stage.size
    return height

  def get_cells(stage):
    width, height = stage.size
    cells = []
    for y in range(height):
      for x in range(width):
        cells.append((x, y))
    return cells

  def get_visible_cells(stage):
    cells = []
    for room in stage.rooms:
      cells += room.get_cells() + room.get_border()
    width, height = stage.size
    maze_cells = []
    for y in range(height):
      for x in range(width):
        if stage.get_tile_at((x, y)) is stage.FLOOR:
          maze_cells.append((x - 1, y - 1))
          maze_cells.append((x + 0, y - 1))
          maze_cells.append((x + 1, y - 1))
          maze_cells.append((x - 1, y + 0))
          maze_cells.append((x + 0, y + 0))
          maze_cells.append((x + 1, y + 0))
          maze_cells.append((x - 1, y + 1))
          maze_cells.append((x + 0, y + 1))
          maze_cells.append((x + 1, y + 1))
    cells += maze_cells
    cells = list(set(cells))
    return cells

  def is_cell_empty(stage, cell):
    if stage.get_tile_at(cell).solid:
      return False
    if stage.get_elem_at(cell):
      return False
    return True

  def is_cell_opaque(stage, cell):
    if stage.get_tile_at(cell).opaque:
      return True
    elem = stage.get_elem_at(cell)
    return elem and elem.opaque

  def get_elem_at(stage, cell, superclass=None):
    if superclass:
      return next((e for e in stage.elems if (
        e.cell == cell
        and (superclass is None or isinstance(e, superclass))
      )), None)
    else:
      return (next((e for e in stage.elems if e.cell == cell and e.solid), None)
        or next((e for e in stage.elems if e.cell == cell and not isinstance(e, Door)), None)
        or next((e for e in stage.elems if e.cell == cell), None))

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

  def spawn_elem(stage, elem, cell=None):
    if elem not in stage.elems:
      stage.elems.append(elem)
    if cell:
      elem.cell = cell

  def remove_elem(stage, elem):
    if elem in stage.elems:
      stage.elems.remove(elem)
      elem.cell = None

  def contains(stage, cell):
    (width, height) = stage.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height
