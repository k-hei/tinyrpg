from pygame import Rect
from config import TILE_SIZE

# TODO: relocate pathfinding logic
from lib.cell import manhattan, neighborhood
from math import inf

class Stage:
  def __init__(stage, tiles, elems=None, rooms=None, links=None, tile_size=TILE_SIZE, bg=None):
    stage.tiles = tiles
    stage.elems = elems or []
    stage.links = links or []
    stage.rooms = rooms or []
    stage.tile_size = tile_size
    stage.bg = bg
    stage.entrance = None
    stage.generator = None
    stage.seed = None

  @property
  def size(stage):
    return stage.tiles.size

  @property
  def width(stage):
    return stage.size[0]

  @property
  def height(stage):
    return stage.size[1]

  @property
  def cells(stage):
    return [(x, y) for y in range(stage.height) for x in range(stage.width)]

  @property
  def border(stage):
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

  def contains(stage, cell):
    return stage.tiles.contains(*cell)

  def get_tile_at(stage, cell):
    return stage.tiles.get(*cell)

  def set_tile_at(stage, cell, tile):
    return stage.tiles.set(*cell, tile)

  def get_elem_at(stage, cell):
    return None

  def get_elems_at(stage, cell):
    return [e for e in stage.elems if (
      e.cell == cell
      or (
        e.size != (1, 1)
        and Rect(e.cell, e.size).collidepoint(cell)
      )
    )]

  def spawn_elem_at(stage, cell, elem):
    elem.spawn(stage, cell)
    if elem not in stage.elems:
      if elem.solid:
        stage.elems.append(elem)
      else:
        stage.elems.insert(0, elem)
    return elem

  def remove_elem(stage, elem):
    if elem in stage.elems:
      stage.elems.remove(elem)
      return True
    else:
      return False

  def is_cell_empty(stage, cell):
    tile = stage.get_tile_at(cell)
    if not tile or tile.solid:
      return False

    elem = next((e for e in stage.get_elems_at(cell) if e.solid), None)
    if elem:
      return False

    return True

  def is_cell_opaque(stage, cell):
    tile = stage.get_tile_at(cell)
    return not tile or tile.opaque or next((e for e in stage.get_elems_at(cell) if e.opaque), None)

  # TODO: normalize into grid pathfinder
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
          open_cells.insert(0, neighbor)
        if neighbor in g and g[cell] + 1 >= g[neighbor]:
          continue
        parent[neighbor] = cell
        g[neighbor] = g[cell] + 1
        f[neighbor] = g[neighbor] + manhattan(neighbor, goal)
        if whitelist and neighbor in whitelist:
          f[neighbor] //= 2
    return []
