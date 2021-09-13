from itertools import product
import random
from random import randint, getrandbits, choice
from pygame.time import get_ticks
from lib.cell import neighborhood, manhattan, is_adjacent, add as add_vector, subtract as subtract_vector
from lib.bounds import find_bounds
import debug
from config import FPS

from dungeon.floors import Floor
from dungeon.features.room import Room
from dungeon.gen import gen_mazeroom, gen_elems
from dungeon.gen.blob import gen_blob
from dungeon.gen.path import gen_path
from dungeon.gen.floorgraph import FloorGraph
from dungeon.stage import Stage
from dungeon.props.door import Door
from dungeon.props.vase import Vase

from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy

from items.hp.potion import Potion
from items.sp.cheese import Cheese
from items.sp.bread import Bread
from items.sp.fish import Fish
from items.dungeon.key import Key
from items.ailment.antidote import Antidote
from items.ailment.musicbox import MusicBox
from items.ailment.lovepotion import LovePotion
from items.ailment.booze import Booze

MIN_ROOM_COUNT = 3
MAX_ROOM_COUNT = 5

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(seed=seed)

def GenRooms(count):
  rooms = []
  while len(rooms) < count:
    cells = next(gen_blob(min_area=80, max_area=200))
    if cells:
      room = Blob(cells)
      rooms.append(room)
    yield None # Performance breakpoint
  yield rooms

def find_connectors(room1, room2):
  inner_overlap = room1.hitbox & room2.hitbox
  if not inner_overlap: # rooms aren't too close
    outer_overlap = room1.hitbox & room2.region
    if outer_overlap: # rooms aren't too far
      return outer_overlap
  return set()

def PlaceRooms(rooms):
  if not rooms:
    yield True
  graph = FloorGraph(nodes=[rooms[0]])
  total_blob = rooms[0]
  connections = {}
  for i, room in enumerate(rooms[1:]):
    # TODO: cache room props internally (subject to change on dependency reset)
    room_rect = room.rect
    total_rect = total_blob.rect
    total_hitbox = total_blob.hitbox
    total_region = total_blob.region

    PADDING = 3
    left = -room_rect.width - PADDING
    right = total_rect.right + PADDING
    top = -room_rect.height - PADDING
    bottom = total_rect.bottom + PADDING
    width = right - left + 1
    height = bottom - top + 1

    valid_origins = []
    for y in range(top, bottom + 1):
      for x in range(left, right + 1):
        valid_origins.append((x, y))

    ticks = get_ticks()
    while valid_origins and room not in graph.nodes:
      room.origin = choice(valid_origins)
      valid_origins.remove(room.origin)
      inner_overlap = total_hitbox & room.hitbox
      if not inner_overlap: # rooms aren't too close
        neighbor_connectors = { n: c for n, c in [(n, find_connectors(n, room)) for n in graph.nodes] if c }
        if len(graph.nodes) < 2:
          if neighbor_connectors:
            neighbor, connectors = [*neighbor_connectors.items()][0]
            graph.add(room)
            graph.connect(room, neighbor, [*connectors][0])
        elif len(neighbor_connectors) >= 2:
          for neighbor, connectors in neighbor_connectors.items():
            graph.add(room)
            graph.connect(room, neighbor, [*connectors][0])
      if (get_ticks() - ticks) > 1000 / FPS * 2:
        ticks = get_ticks()
        if room in graph.nodes:
          yield graph, f"Placed room {len(graph.nodes)} of {len(rooms)}"
        else:
          yield graph, f"Placing room {len(graph.nodes) + 1} of {len(rooms)} ({width * height - len(valid_origins)}/{width * height})"

    if room not in graph.nodes:
      yield False, "Failed to place rooms"

    total_blob = Blob(total_blob.cells + room.cells)

  yield graph, ""

def gen_floor(
  enemies=[Eyeball, Mushroom, Ghost, Mummy],
  items=[Potion, Cheese, Bread, Fish, Antidote, MusicBox, LovePotion, Booze],
  seed=None
):
  seed = seed or getrandbits(32)
  random.seed(seed)

  lkg = None
  while lkg is None:
    rooms = None
    gen_rooms = GenRooms(count=randint(MIN_ROOM_COUNT, MAX_ROOM_COUNT))
    while rooms is None:
      rooms = next(gen_rooms)
      yield None, "Generating rooms"

    graph, message = {}, "*"
    place_rooms = PlaceRooms(rooms)
    while message and graph is not False:
      graph, message = next(place_rooms)
      if graph is not False:
        yield None, message

    stage_cells = []
    for room in rooms:
      stage_cells += room.cells

    stage_offset = subtract_vector(find_bounds(stage_cells).topleft, (1, 1))
    for room in rooms:
      room.origin = subtract_vector(room.origin, stage_offset)

    stage_blob = Blob(stage_cells, origin=(1, 1))
    stage = Stage(add_vector(stage_blob.rect.size, (2, 2)))
    stage.seed = seed
    stage.fill(Stage.WALL)
    for cell in stage_blob.cells:
      stage.set_tile_at(cell, Stage.FLOOR)

    if graph is False:
      yield stage, message
      continue

    connected = True
    door_paths = set()
    for i, ((room1, room2), [connector]) in enumerate(graph.connections()):
      connector = subtract_vector(connector, stage_offset)

      distance_from_connector = lambda e: manhattan(e, connector)
      is_edge_usable = lambda e, room: (
        not next((n for n in neighborhood(e, radius=2) if next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)), None)
        and len([n for n in neighborhood(e) if stage.get_tile_at(n) is Stage.WALL]) == 3
        and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is Stage.WALL]) in (5, 6, 7)
        # and not next((c for c in [c for r in [r for r in rooms if r is not room] for c in r.outline] if is_adjacent(c, e)), None)
        and not e in stage.get_border()
      )

      prev_edges = [e for e in room1.edges if is_edge_usable(e, room=room1)]
      if not prev_edges:
        yield stage, f"Failed to find usable edges for room {i + 1}"
        connected = False
        break
      prev_edges.sort(key=distance_from_connector)

      room_edges = [e for e in room2.edges if is_edge_usable(e, room=room2)]
      if not room_edges:
        yield stage, f"Failed to find usable edges for room {i + 2}"
        connected = False
        break
      room_edges.sort(key=distance_from_connector)

      print(f"Connecting {room1.origin} and {room2.origin} using {connector}")
      room_outlines = [c for r in rooms for c in r.outline]
      for door1, door2 in product(prev_edges, room_edges):
        if (door1 in prev_edges and door2 in prev_edges
        or door1 in room_edges and door2 in room_edges):
          continue

        door1_neighbor = next((n for n in neighborhood(door1) if n in room1.cells), None)
        door1_delta = subtract_vector(door1, door1_neighbor)
        door1_start = add_vector(door1, door1_delta)

        door2_neighbor = next((n for n in neighborhood(door2) if n in room2.cells), None)
        door2_delta = subtract_vector(door2, door2_neighbor)
        door2_start = add_vector(door2, door2_delta)

        path_blacklist = (set(room_outlines + stage.get_border()) - {door1_start, door2_start}) | door_paths
        door_path = gen_path(door1_start, door2_start, predicate=lambda cell: cell not in path_blacklist)
        if door_path:
          break

      if not door_path:
        yield stage, f"Failed to path between rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1}"
        connected = False
        break

      door_path = [door1] + door_path + [door2]
      stage.spawn_elem_at(door1, Door())
      stage.spawn_elem_at(door2, Door())
      for cell in door_path:
        if cell in (door1, door1_start, door2, door2_start):
          tile = Stage.DOOR_WAY
        else:
          tile = Stage.FLOOR
        stage.set_tile_at(cell, tile)
        door_paths.update(neighborhood(cell, inclusive=True, diagonals=True))
      print(f"Connected {room1.origin} and {room2.origin} using {connector} via {door1} and {door2}")
      yield stage, f"Connected rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1}"

    if not connected:
      continue

    for room in rooms:
      gen_mazeroom(stage, room)

    empty_rooms = rooms.copy()
    for room in sorted(rooms, key=lambda r: r.get_area()):
      entrances = [c for c in room.cells if not next((n for n in neighborhood(c, radius=1) if stage.get_tile_at(n) is not Stage.FLOOR), None)]
      if entrances:
        stage.entrance = choice(entrances)
        stage.set_tile_at(stage.entrance, Stage.STAIRS_UP)
        empty_rooms.remove(room)
        yield stage, f"Spawned entrance at {stage.entrance}"
        break
    else:
      yield stage, "Failed to spawn entrance"

    for i, room in enumerate(empty_rooms):
      yield stage, f"Spawning items for room {i + 2}"
      items_spawned = gen_elems(stage, room,
        elems=[Vase(choice(items)) for _ in range(min(3, room.get_area() // 20))]
      )
      yield stage, f"Spawning enemies for room {i + 2}"
      enemies_spawned = gen_elems(stage, room,
        elems=[choice(enemies)() for _ in range(min(6, room.get_area() // 20))]
      )

    stage.rooms = rooms
    lkg = stage
    break

  yield stage, ""

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
      neighbors = neighborhood(cell, diagonals=True, radius=2)
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
    return list(blob.outline)

  def get_center(blob):
    return blob.rect.center

  def get_outline(blob):
    return list(blob.outline)

  def find_closest_cell(blob, dest):
    return sorted(blob.cells, key=lambda c: manhattan(c, dest))[0]
