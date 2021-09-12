from random import randint, choice
from pygame.time import get_ticks
from lib.cell import neighborhood, manhattan, is_adjacent, add as add_vector, subtract as subtract_vector
from lib.bounds import find_bounds
import debug

from dungeon.floors import Floor
from dungeon.features.room import Room
from dungeon.gen import gen_mazeroom
from dungeon.gen.blob import gen_blob
from dungeon.gen.path import gen_path
from dungeon.gen.floorgraph import FloorGraph
from dungeon.stage import Stage
from dungeon.props.door import Door

from config import FPS

class DebugFloor(Floor):
  def generate(store):
    return gen_floor()

def GenRooms():
  rooms = []
  while len(rooms) < 4:
    cells = next(gen_blob(min_area=80, max_area=200))
    if cells:
      room = Blob(cells)
      rooms.append(room)
    yield None # Performance breakpoint
  yield rooms

def PlaceRooms(rooms):
  if not rooms:
    yield True
  prev_room = rooms[0]
  placed_rooms = [prev_room]
  connections = {}
  for i, room in enumerate(rooms[1:]):
    connections[i] = {}
    # TODO: cache room props internally (subject to change on dependency reset)
    room_rect = room.rect
    prev_rect = prev_room.rect
    prev_hitbox = prev_room.hitbox
    prev_border = prev_room.border
    ticks = get_ticks()
    for y in range(-room_rect.height - 1, prev_rect.bottom + 1):
      for x in range(-room_rect.width - 1, prev_rect.right + 1):
        room.origin = (x, y)
        body_overlap = set(prev_hitbox) & set(room.hitbox)
        if not body_overlap:
          border_overlap = set(prev_border) & set(room.border)
          if border_overlap:
            connections[i][(x, y)] = border_overlap
        if get_ticks() - ticks > 1000 / FPS:
          ticks = get_ticks()
          yield None # Performance breakpoint
    if not connections[i]:
      yield False
    room.origin = choice([*connections[i].keys()])
    prev_room = Blob(prev_room.cells + room.cells)
  yield connections

def gen_floor():
  lkg = None
  while lkg is None:
    rooms = None
    gen_rooms = GenRooms()
    while rooms is None:
      rooms = next(gen_rooms)
      yield None

    connections = None
    place_rooms = PlaceRooms(rooms)
    while connections is None:
      connections = next(place_rooms)
      yield None
    if connections is False:
      debug.log("Failed to place rooms")
      continue

    stage_cells = []
    for room in rooms:
      stage_cells += room.cells

    stage_offset = subtract_vector(find_bounds(stage_cells).topleft, (1, 1))
    stage_blob = Blob(stage_cells, origin=(1, 1))
    stage = Stage(add_vector(stage_blob.rect.size, (2, 2)))
    stage.fill(Stage.WALL)
    for cell in stage_blob.cells:
      stage.set_tile_at(cell, Stage.FLOOR)
    stage.entrance = (0, 0)

    # Origin is used to key into connections map
    rooms[0].origin = subtract_vector(rooms[0].origin, stage_offset)

    connected = True
    door_paths = []
    for i, room in enumerate(rooms[1:]):
      connector = choice([*connections[i][room.origin]])
      connector = subtract_vector(connector, stage_offset)
      room.origin = subtract_vector(room.origin, stage_offset)

      distance_from_connector = lambda e: manhattan(e, connector)
      is_edge_usable = lambda e, other_room: (
        not next((n for n in neighborhood(e, radius=2) if next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)), None)
        and len([n for n in neighborhood(e) if stage.get_tile_at(n) is Stage.WALL]) == 3
        and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is Stage.WALL]) in (5, 6, 7)
        and not next((c for c in other_room.outline if is_adjacent(c, e)), None)
      )

      prev_room = rooms[i]
      prev_edges = [e for e in prev_room.edges if is_edge_usable(e, other_room=room)]
      if not prev_edges:
        debug.log("Failed to create usable door edges")
        connected = False
        break
      door1 = sorted(prev_edges, key=distance_from_connector)[0]
      door1_neighbor = next((n for n in neighborhood(door1) if n in prev_room.cells), None)
      door1_delta = subtract_vector(door1, door1_neighbor)
      door1_start = add_vector(door1, door1_delta)
      stage.spawn_elem_at(door1, Door())

      room_edges = [e for e in room.edges if is_edge_usable(e, other_room=prev_room)]
      if not room_edges:
        debug.log("Failed to create usable door edges")
        connected = False
        break
      door2 = sorted(room_edges, key=distance_from_connector)[0]
      door2_neighbor = next((n for n in neighborhood(door2) if n in room.cells), None)
      door2_delta = subtract_vector(door2, door2_neighbor)
      door2_start = add_vector(door2, door2_delta)
      stage.spawn_elem_at(door2, Door())

      path_blacklist = set(prev_room.outline + room.outline + stage.get_border() + door_paths) - {door1_start, door2_start}
      door_path = gen_path(door1_start, door2_start, predicate=lambda cell: cell not in path_blacklist)
      if not door_path:
        debug.log(f"Failed to path between doors {i} and {i + 1}")
        connected = False
        break
      door_path = [door1] + door_path + [door2]
      for cell in door_path:
        stage.set_tile_at(cell, Stage.STAIRS_UP)
      door_paths += door_path
      # gen_mazeroom(stage, room)

    if not connected:
      yield None
      continue

    stage.entrance = choice(rooms[0].cells)
    stage.rooms = rooms
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
        # + neighborhood(add_vector(cell, (0, 1)), diagonals=True)
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

  def get_edges(blob):
    return blob.edges

  def get_border(blob):
    return blob.outline
