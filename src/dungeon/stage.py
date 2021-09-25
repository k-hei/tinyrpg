from math import inf
from dataclasses import dataclass
from lib.cell import neighborhood, manhattan

@dataclass
class Tile:
  solid: bool = False
  opaque: bool = False
  elev: float = 0.0
  direction: tuple = (0, 0)

  def is_solid(tile):
    return tile and tile.solid

  def is_opaque(tile):
    return not tile or tile.opaque

  def get_elev(tile):
    return tile and tile.elev or 0

class Stage:
  class FLOOR(Tile):
    solid = False
    opaque = False

  class WALL(Tile):
    solid = True
    opaque = True

  class FLOOR_ELEV(Tile):
    solid = False
    opaque = False
    elev = 1.0

  class WALL_ELEV(Tile):
    solid = True
    opaque = False

  class STAIRS(Tile):
    solid = False
    opaque = False
    elev = 0.5
    direction = (0, -1)

  class STAIRS_LEFT(Tile):
    elev = 0.5
    direction = (-1, 0)

  class STAIRS_RIGHT(Tile):
    solid = False
    opaque = False
    elev = 0.5
    direction = (1, 0)

  class LADDER(Tile):
    solid = False
    opaque = False
    elev = 0.5

  class PIT(Tile):
    solid = True
    opaque = False

  class HALLWAY(Tile):
    solid = False
    opaque = False

  class STAIRS_UP(Tile):
    solid = False
    opaque = False

  class STAIRS_DOWN(Tile):
    solid = False
    opaque = False

  class OASIS(Tile):
    solid = False
    opaque = False
    elev = -1.0

  class OASIS_STAIRS(Tile):
    solid = False
    opaque = False
    elev = -0.5

  class STAIRS_EXIT(Tile):
    solid = False
    opaque = False

  TILES = [PIT, FLOOR, WALL, STAIRS_DOWN, STAIRS_UP, HALLWAY, OASIS, OASIS_STAIRS]
  TILE_ORDER = [FLOOR, WALL, PIT, STAIRS_DOWN, STAIRS_UP, STAIRS_EXIT, HALLWAY, OASIS, OASIS_STAIRS]

  def __init__(stage, size, data=None, elems=None):
    width, height = size
    stage.size = size
    stage.data = data or [Stage.FLOOR] * (width * height)
    stage.elems = elems or []
    stage.rooms = []
    stage.decors = []
    stage.entrance = None
    stage.exit = None
    stage.generator = None
    stage.seed = None

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

  def get_border(stage):
    border = []
    width, height = stage.size
    for y in range(height):
      border += [
        (0, y),
        (width - 1, y)
      ]
    for x in range(height):
      border += [
        (x, 0),
        (x, height - 1)
      ]
    return border

  def get_visible_cells(stage):
    cells = []
    for room in stage.rooms:
      cells += room.get_cells() + room.get_outline()
    width, height = stage.size
    for y in range(height):
      for x in range(width):
        if stage.get_tile_at((x, y)) is stage.HALLWAY:
          cells += neighborhood((x, y), inclusive=True, diagonals=True)
    return [*set(cells)]

  def is_cell_empty(stage, cell):
    target_tile = stage.get_tile_at(cell)
    if not target_tile or target_tile.solid:
      return False
    target_elem = stage.get_elem_at(cell)
    if target_elem and target_elem.solid:
      return False
    return True

  def is_cell_opaque(stage, cell):
    if stage.get_tile_at(cell).opaque:
      return True
    elem = stage.get_elem_at(cell)
    return elem and elem.opaque

  def get_elems_at(stage, cell):
    return [e for e in stage.elems if e.cell == cell]

  def get_elem_at(stage, cell, superclass=None, exclude=[]):
    if superclass:
      return next((e for e in stage.elems if (
        e.cell == cell
        and isinstance(e, superclass)
        and not next((t for t in exclude if isinstance(e, t)), None)
      )), None)
    else:
      return (
        next((e for e in stage.elems if (
          e.cell == cell
          and e.solid
          and not next((t for t in exclude if isinstance(e, t)), None)
        )), None)
        or next((e for e in stage.elems if (
          e.cell == cell
          and not next((t for t in exclude if isinstance(e, t)), None)
        )), None)
      )

  def get_tile_at(stage, cell):
    if not stage.contains(cell):
      return None
    width = stage.get_width()
    x, y = cell
    return stage.data[y * width + x]

  def set_tile_at(stage, cell, data):
    if not stage.contains(cell):
      return
    width = stage.size[0]
    x, y = cell
    stage.data[y * width + x] = data

  def spawn_elem_at(stage, cell, elem):
    elem.spawn(stage, cell)
    if elem not in stage.elems:
      stage.elems.append(elem)
    return elem

  def remove_elem(stage, elem):
    if elem in stage.elems:
      stage.elems.remove(elem)
      elem.cell = None

  def find_tile(stage, tile):
    width, height = stage.size
    for y in range(height):
      for x in range(width):
        cell = (x, y)
        if stage.get_tile_at(cell) is tile:
          return cell
    return None

  def find_elem(stage, cls):
    width, height = stage.size
    for y in range(height):
      for x in range(width):
        cell = (x, y)
        elem = stage.get_elem_at(cell, superclass=cls)
        if elem:
          return elem
    return None

  def contains(stage, cell):
    (width, height) = stage.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height

  def pathfind(stage, start, goal, whitelist=None):
    if start == goal:
      return [goal]
    path = []
    open_cells = [start]
    open_set = {}
    closed_set = {}
    f = { start: manhattan(start, goal) }
    g = { start: 0 }
    parent = {}
    while open_cells:
      open_cells.sort(key=lambda c: f[c] if c in f else inf)
      cell = open_cells.pop(0)
      if cell == goal:
        while cell != start:
          path.insert(0, cell)
          cell = parent[cell]
        path.insert(0, cell)
        return path
      open_set[cell] = False
      closed_set[cell] = True
      for neighbor in neighborhood(cell):
        if (neighbor in closed_set
        or not stage.contains(neighbor)
        or (not stage.is_cell_empty(neighbor) and (not whitelist or neighbor not in whitelist))
        ):
          continue
        if neighbor not in open_set or not open_set[neighbor]:
          open_set[neighbor] = True
          open_cells.append(neighbor)
        if neighbor in g and g[cell] + 1 >= g[neighbor]:
          continue
        parent[neighbor] = cell
        g[neighbor] = g[cell] + 1
        f[neighbor] = g[neighbor] + manhattan(neighbor, goal)
        if whitelist and neighbor in whitelist:
          f[neighbor] //= 2
    return []
