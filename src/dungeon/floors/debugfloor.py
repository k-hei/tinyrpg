from itertools import product
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
  def generate(store=None):
    return gen_floor()

def GenRooms(count):
  rooms = []
  while len(rooms) < count:
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
    # TODO: cache room props internally (subject to change on dependency reset)
    room_rect = room.rect
    prev_rect = prev_room.rect
    prev_hitbox = prev_room.hitbox
    prev_region = prev_room.region

    PADDING = 3
    left = -room_rect.width - PADDING
    right = prev_rect.right + PADDING
    top = -room_rect.height - PADDING
    bottom = prev_rect.bottom + PADDING
    width = right - left + 1
    height = bottom - top + 1

    valid_origins = []
    for y in range(top, bottom + 1):
      for x in range(left, right + 1):
        valid_origins.append((x, y))

    ticks = get_ticks()
    while valid_origins:
      room.origin = choice(valid_origins)
      valid_origins.remove(room.origin)
      body_overlap = prev_hitbox & room.hitbox
      if not body_overlap: # rooms aren't too close
        region_overlap = prev_region & room.region
        if region_overlap: # rooms aren't too far
          connections[i] = room.origin
      if (get_ticks() - ticks) > 1000 / FPS * 2:
        ticks = get_ticks()
        percent = int((1 - len(valid_origins) / (width * height)) * 100)
        yield connections, f"Placing room {len(connections) + 1} of {len(rooms)} ({percent}%)" # Performance breakpoint

    if i not in connections:
      yield False, "Failed to place rooms"

    room.origin = connections[i]
    prev_room = Blob(prev_room.cells + room.cells)

  yield connections, ""

def gen_floor():
  lkg = None
  while lkg is None:
    rooms = None
    gen_rooms = GenRooms(count=4)
    while rooms is None:
      rooms = next(gen_rooms)
      yield None, "Generating rooms"

    connections, message = {}, "*"
    connections_size = 0
    place_rooms = PlaceRooms(rooms)
    while message and connections is not False:
      if len(connections) != connections_size:
        connections_size = len(connections)
      connections, message = next(place_rooms)
      yield None, message
    if connections is False:
      continue

    stage_cells = []
    for room in rooms:
      stage_cells += room.cells

    stage_offset = subtract_vector(find_bounds(stage_cells).topleft, (1, 1))
    for room in rooms:
      room.origin = subtract_vector(room.origin, stage_offset)

    stage_blob = Blob(stage_cells, origin=(1, 1))
    stage = Stage(add_vector(stage_blob.rect.size, (2, 2)))
    stage.fill(Stage.WALL)
    for cell in stage_blob.cells:
      stage.set_tile_at(cell, Stage.FLOOR)
    stage.entrance = choice(rooms[0].cells)
    stage.set_tile_at(stage.entrance, Stage.STAIRS_UP)

    connected = True
    door_paths = []
    for i, room in enumerate(rooms[1:]):
      connector = connections[i]
      connector = subtract_vector(connector, stage_offset)

      distance_from_connector = lambda e: manhattan(e, connector)
      is_edge_usable = lambda e, room: (
        not next((n for n in neighborhood(e, radius=2) if next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)), None)
        and len([n for n in neighborhood(e) if stage.get_tile_at(n) is Stage.WALL]) == 3
        and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is Stage.WALL]) in (5, 6, 7)
        and not next((c for c in [c for r in [r for r in rooms if r is not room] for c in r.outline] if is_adjacent(c, e)), None)
      )

      prev_room = rooms[i]
      prev_edges = [e for e in prev_room.edges if is_edge_usable(e, room=prev_room)]
      if not prev_edges:
        yield stage, f"Failed to find usable edges for room {i + 1}"
        connected = False
        break
      prev_edges.sort(key=distance_from_connector)

      room_edges = [e for e in room.edges if is_edge_usable(e, room)]
      if not room_edges:
        yield stage, f"Failed to find usable edges for room {i + 2}"
        connected = False
        break
      room_edges.sort(key=distance_from_connector)

      room_outlines = [c for r in rooms for c in r.outline]
      for door1, door2 in product(prev_edges, room_edges):
        door1_neighbor = next((n for n in neighborhood(door1) if n in prev_room.cells), None)
        door1_delta = subtract_vector(door1, door1_neighbor)
        door1_start = add_vector(door1, door1_delta)

        door2_neighbor = next((n for n in neighborhood(door2) if n in room.cells), None)
        door2_delta = subtract_vector(door2, door2_neighbor)
        door2_start = add_vector(door2, door2_delta)

        path_blacklist = set(room_outlines + stage.get_border() + door_paths) - {door1_start, door2_start}
        door_path = gen_path(door1_start, door2_start, predicate=lambda cell: cell not in path_blacklist)
        if door_path:
          break

      if not door_path:
        yield stage, "Failed to path between rooms"
        connected = False
        break

      door_path = [door1] + door_path + [door2]
      stage.spawn_elem_at(door1, Door())
      stage.spawn_elem_at(door2, Door())
      for cell in door_path:
        stage.set_tile_at(cell, Stage.STAIRS_UP)
      door_paths += door_path

      # gen_mazeroom(stage, room)

    if not connected:
      continue

    stage.rooms = rooms
    lkg = stage

  yield lkg, ""

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
    hitbox = []
    for cell in blob.cells:
      neighbors = neighborhood(cell, diagonals=True)
      hitbox += neighbors
    return set(hitbox)

  @property
  def edges(blob):
    edges = set()
    for cell in blob.cells:
      neighbors = neighborhood(cell)
      edges.update(neighbors)
    return list(edges - set(blob.cells))

  @property
  def region(blob):
    region = []
    for cell in blob.cells:
      neighbors = neighborhood(cell, radius=3)
      region += neighbors
    return set(region)

  @property
  def outline(blob):
    outline = []
    for cell in blob.cells:
      neighbors = (
        neighborhood(cell, diagonals=True)
        + neighborhood(add_vector(cell, (0, -1)), diagonals=True)
        # + neighborhood(add_vector(cell, (0, 1)), diagonals=True)
      )
      outline += neighbors
    return set(outline) - set(blob.cells)

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
