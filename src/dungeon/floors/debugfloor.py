from random import randint, choice
from lib.cell import neighborhood, manhattan, is_adjacent, add as add_vector, subtract as subtract_vector
from lib.bounds import find_bounds
import debug

from dungeon.floors import Floor
from dungeon.features.room import Room
from dungeon.gen.blob import gen_blob
from dungeon.gen.path import gen_path
from dungeon.stage import Stage
from dungeon.props.door import Door

class DebugFloor(Floor):
  def generate(store):
    return gen_floor()

def gen_floor():
  lkg = None
  while lkg is None:
    blob1 = next(gen_blob())
    if blob1 is None:
      debug.log("Failed to generate room")
      yield None
      continue
    blob1 = Blob(blob1)
    yield None # Performance breakpoint

    blob2 = next(gen_blob(min_area=60, max_area=120))
    if blob2 is None:
      debug.log("Failed to generate room")
      yield None
      continue
    blob2 = Blob(blob2)
    yield None # Performance breakpoint

    connections = {}
    for y in range(-blob2.rect.height, blob1.rect.bottom):
      for x in range(-blob2.rect.width, blob1.rect.right):
        blob2.origin = (x, y)
        body_overlap = set(blob1.hitbox) & set(blob2.hitbox)
        if not body_overlap:
          border_overlap = set(blob1.border) & set(blob2.border)
          if border_overlap:
            connections[(x, y)] = border_overlap
      yield None # Performance breakpoint

    if not connections:
      debug.log("Failed to connect rooms")
      yield None
      continue

    origin = choice(list(connections.keys()))
    blob2.origin = origin
    blob3_cells = blob1.cells + blob2.cells
    blob3_offset = add_vector(find_bounds(blob3_cells).topleft, (-1, -1))
    blob3 = Blob(blob3_cells, origin=(1, 1))
    blob1.origin = add_vector(blob1.origin, tuple([-x for x in blob3_offset]))
    blob2.origin = add_vector(blob2.origin, tuple([-x for x in blob3_offset]))

    stage = Stage(add_vector(blob3.rect.size, (2, 2)))
    stage.fill(Stage.WALL)
    for cell in blob3.cells:
      stage.set_tile_at(cell, Stage.FLOOR)

    connector = choice([*connections[origin]])
    connector = add_vector(connector, tuple([-x for x in blob3_offset]))

    distance_from_connector = lambda e: manhattan(e, connector)
    is_edge_usable = lambda e, other_blob: (
      not next((n for n in neighborhood(e, radius=2) if next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)), None)
      and len([n for n in neighborhood(e) if stage.get_tile_at(n) is Stage.WALL]) == 3
      and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is Stage.WALL]) in (5, 6, 7)
      and not next((c for c in other_blob.outline if is_adjacent(c, e)), None)
    )

    blob1_edges = [e for e in blob1.edges if is_edge_usable(e, other_blob=blob2)]
    if not blob1_edges:
      debug.log("Failed to create usable door edges")
      yield None
      continue
    door1 = sorted(blob1_edges, key=distance_from_connector)[0]
    door1_neighbor = next((n for n in neighborhood(door1) if n in blob1.cells), None)
    door1_delta = subtract_vector(door1, door1_neighbor)
    door1_start = add_vector(door1, door1_delta)
    stage.spawn_elem_at(door1, Door())

    blob2_edges = [e for e in blob2.edges if is_edge_usable(e, other_blob=blob1)]
    if not blob2_edges:
      debug.log("Failed to create usable door edges")
      yield None
      continue
    door2 = sorted(blob2_edges, key=distance_from_connector)[0]
    door2_neighbor = next((n for n in neighborhood(door2) if n in blob2.cells), None)
    door2_delta = subtract_vector(door2, door2_neighbor)
    door2_start = add_vector(door2, door2_delta)
    stage.spawn_elem_at(door2, Door())

    path_blacklist = set(blob1.outline + blob2.outline + stage.get_border()) - {door1_start, door2_start}
    door_path = gen_path(door1_start, door2_start, predicate=lambda cell: cell not in path_blacklist)
    if not door_path:
      debug.log("Failed to path between doors")
      yield None
      continue
    door_path = [door1] + door_path + [door2]
    for cell in door_path:
      stage.set_tile_at(cell, Stage.FLOOR)

    stage.entrance = choice(blob1.cells)
    stage.rooms += [blob1, blob2]
    lkg = stage

  yield lkg

def find_border(cells):
  border = set()
  for cell in cells:
    border |= neighborhood(cell)
  return list(border)

class Blob(Room):
  def __init__(blob, cells, origin=None):
    rect = find_bounds(cells)
    left, top = rect.topleft
    blob.origin = origin or (left, top)
    blob._cells = [add_vector(c, (-left, -top)) for c in cells]
    super().__init__(size=rect.size, cell=blob.origin)

  @property
  def cells(blob):
    return [add_vector(c, blob.origin) for c in blob._cells]

  @property
  def hitbox(blob):
    hitbox = set()
    for cell in blob.cells:
      neighbors = neighborhood(cell, diagonals=True)
      hitbox.update(neighbors)
    return list(hitbox)

  @property
  def edges(blob):
    edges = set()
    for cell in blob.cells:
      neighbors = neighborhood(cell)
      edges.update(neighbors)
    return list(edges - set(blob.cells))

  @property
  def border(blob):
    border = set()
    for cell in blob.cells:
      neighbors = neighborhood(cell, radius=2)
      border.update(neighbors)
    return list(border)

  @property
  def outline(blob):
    outline = set()
    for cell in blob.cells:
      neighbors = (
        neighborhood(cell, diagonals=True)
        + neighborhood(add_vector(cell, (0, -1)), diagonals=True)
        + neighborhood(add_vector(cell, (0, 1)), diagonals=True)
      )
      outline.update(neighbors)
    return list(outline)

  @property
  def rect(blob):
    return find_bounds(blob.cells)

  @property
  def cell(blob):
    return blob.origin

  @cell.setter
  def cell(blob, cell):
    blob.origin = cell

  def get_width(blob):
    return blob.rect.width

  def get_height(blob):
    return blob.rect.height

  def get_cells(blob):
    return blob.cells

  def get_border(blob):
    return blob.outline
