from pygame import Rect
from config import TILE_SIZE
from locations.default.tile import Tile
from dungeon.actors import DungeonActor

# TODO: relocate pathfinding logic
import lib.vector as vector
from lib.cell import manhattan, neighborhood, downscale
from math import inf


class Stage:
  def __init__(stage, tiles, tileset=None, elems=None, rooms=None, ports=None, tile_size=None, bg=None, name="????"):
    stage.name = name
    stage.tileset = tileset
    stage.tiles = tiles
    stage.elems = elems or []
    stage.ports = ports or []
    stage.rooms = rooms or []
    stage.tile_size = tile_size or (tileset and tileset.tile_size) or TILE_SIZE
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

  @property
  def num_tile_layers(stage):
    return stage.tiles.num_layers

  @property
  def is_overworld(stage):
    return stage.tileset.is_overworld

  def __contains__(stage, cell):
    return stage.contains(cell)

  def contains(stage, cell, scale=0):
    if scale:
      scale_delta = scale / stage.tile_size
      scale_cell = vector.floor(vector.scale(cell, scale_delta))
      return scale_cell in stage

    return cell in stage.tiles

  def get_tile_at(stage, cell):
    tiles = stage.get_tiles_at(cell)
    return tiles[0] if tiles else None

  def get_tiles_at(stage, cell, scale=0):
    if cell not in stage:
      return []

    if not scale:
      return stage.tiles[cell]

    scale_delta = scale // stage.tile_size
    origin_cell = vector.scale(cell, scale_delta)
    offsets = [(x, y) for y in range(scale_delta) for x in range(scale_delta)]
    cells = [vector.add(origin_cell, o) for o in offsets]
    return [t for c in cells for t in stage.get_tiles_at(c)]

  def set_tile_at(stage, cell, tile):
    stage.tiles[cell] = tile

  def is_tile_at_of_type(stage, cell, tile_type):
    return next((t for t in stage.get_tiles_at(cell)
      if Tile.is_of_type(t, tile_type)), None)

  def is_tile_at_solid(stage, cell, scale=0):
    if cell not in stage:
      return True

    tiles = stage.get_tiles_at(cell, scale)
    return not tiles or next((True for tile in tiles if stage.tileset.is_tile_at_solid(tile)), False)

  def is_tile_at_wall(stage, cell):
    return stage.tileset.is_tile_at_wall(tile=stage.get_tile_at(cell))

  def is_tile_at_pit(stage, cell):
    return stage.tileset.is_tile_at_pit(tile=stage.get_tile_at(cell))

  def is_tile_at_hallway(stage, cell):
    return stage.tileset.is_tile_at_hallway(tile=stage.get_tile_at(cell))

  def is_tile_at_oasis(stage, cell):
    return stage.tileset.is_tile_at_oasis(tile=stage.get_tile_at(cell))

  def is_tile_at_port(stage, cell):
    return stage.tileset.is_tile_at_port(tile=stage.get_tile_at(cell))

  def get_tile_at_elev(stage, cell):
    tile = stage.get_tile_at(cell)
    return tile.elev if Tile.is_tile(tile) else 0

  def get_elem_at(stage, cell):
    return None

  def get_elems_at(stage, cell, scale=0):

    def is_elem_at_cell(elem, cell):
      return (elem.cell == cell
        or (elem.size != (1, 1)
          and Rect(elem.cell, elem.size).collidepoint(cell)
        )
      )

    return [e for e in stage.elems if is_elem_at_cell(
      elem=e,
      cell=cell,
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

  def is_cell_empty(stage, cell, scale=0):
    return (not stage.is_tile_at_solid(cell, scale)
      and not stage.is_cell_occupied(cell, scale))

  def is_cell_occupied(stage, cell, scale=0, ignore_actors=False):
    return next((True for e in stage.get_elems_at(cell, scale)
      if e.solid
      and (not ignore_actors or not isinstance(e, DungeonActor))
    ), False)

  def is_cell_opaque(stage, cell):
    tile = stage.get_tile_at(cell)
    return not tile or stage.tileset.is_tile_at_opaque(tile=stage.get_tile_at(cell)) or next((e for e in stage.get_elems_at(cell) if e.opaque), None)

  def is_cell_walkable(stage, cell, scale=0):
    if not stage.contains(cell, scale):
      return False

    # TODO: handle floating enemies -- walkability is actor-dependent
    return (not stage.is_tile_at_solid(cell, scale)
      and not stage.is_tile_at_pit(cell))

  # TODO: normalize into grid pathfinder
  def pathfind(stage, start, goal, whitelist=None, predicate=None):
    if start == goal:
      return [goal]

    path = []
    open_cells = [start]
    open_set = {}
    closed_set = {}
    f = { start: manhattan(start, goal) }
    g = { start: 0 }
    parent = {}

    num_visits = 0

    while open_cells:
      open_cells.sort(key=lambda c: f[c] if c in f else inf)
      cell = open_cells.pop(0)
      num_visits += 1

      if cell == goal:
        # reconstruct path
        while cell != start:
          path.insert(0, cell)
          cell = parent[cell]
        path.insert(0, cell)
        print("pathfind", start, goal, "in", num_visits, "visits")
        return path

      open_set[cell] = False
      closed_set[cell] = True

      for neighbor in neighborhood(cell):
        if neighbor != goal and (neighbor in closed_set
        or not stage.contains(neighbor, scale=TILE_SIZE)):
          continue

        if predicate and not predicate(neighbor):
          continue

        if (not predicate
        and not stage.is_cell_empty(neighbor, scale=TILE_SIZE)
        and (not whitelist or neighbor not in whitelist)):
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
          # prefer whitelisted cells
          f[neighbor] //= 2

    # no path found
    return []

  def find_walkable_room_cells(stage, room=None, cell=None, ignore_actors=False):
    room = room or next((r for r in stage.rooms if cell in r.cells), None)
    return [c for c in room.cells if (
      (stage.is_cell_walkable(c)
        and not next((e for e in stage.get_elems_at(c) if e.solid and not isinstance(e, DungeonActor)), None)
      ) if ignore_actors else stage.is_cell_walkable(c)
    )] if room else []

  # TODO: relocate into helper
  def find_elem(stage, cls):
    return next((e for c in stage.cells for e in stage.get_elems_at(c) if (
      type(cls) is type and isinstance(e, cls)
      or type(cls) is str and type(e).__name__ == cls
    )), None)
