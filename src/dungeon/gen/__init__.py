from math import inf
from itertools import product
import random
from random import randint, getrandbits, choice, shuffle
from pygame.time import get_ticks
from lib.cell import neighborhood, manhattan, is_adjacent, add as add_vector, subtract as subtract_vector
import debug
import assets
from config import FPS

from dungeon.floors import Floor
from dungeon.room import Blob
from dungeon.gen.terrain import gen_terrain
from dungeon.gen.elems import gen_elems
from dungeon.gen.blob import gen_blob
from dungeon.gen.path import gen_path
from dungeon.gen.manifest import manifest_stage
from dungeon.gen.floorgraph import FloorGraph
from dungeon.stage import Stage
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.vase import Vase
from dungeon.props.chest import Chest
from dungeon.props.arrowtrap import ArrowTrap

from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy

from items.ailment.amethyst import Amethyst
from items.ailment.antidote import Antidote
from items.ailment.booze import Booze
from items.ailment.lovepotion import LovePotion
from items.ailment.musicbox import MusicBox
from items.ailment.topaz import Topaz
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.hp.ruby import Ruby
from items.sp.berry import Berry
from items.sp.bread import Bread
from items.sp.cheese import Cheese
from items.sp.fish import Fish
from items.sp.sapphire import Sapphire
from skills.weapon.longinus import Longinus

from resolve.event import resolve_event

ENABLE_LOOPLESS_LAYOUTS = False
MIN_ROOM_COUNT = 12 if ENABLE_LOOPLESS_LAYOUTS else 8
MAX_ROOM_COUNT = MIN_ROOM_COUNT + 2
ALL_ITEMS = [
  Amethyst,
  Antidote, Antidote,
  Booze,
  LovePotion,
  MusicBox,
  Topaz,
  Balloon,
  Emerald,
  Ankh,
  Elixir,
  Potion, Potion,
  Ruby,
  Berry,
  Bread, Bread,
  Cheese, Cheese,
  Fish, Fish,
  Sapphire
]

def gen_rooms(count, init=None):
  rooms = init or []
  while len(rooms) < count:
    blob_gen = (
      len(rooms) > count // 3
      and gen_blob(min_area=80, max_area=100)
      or gen_blob(min_area=150, max_area=240)
    )
    cells = None
    while not cells:
      cells = next(blob_gen)
      if cells:
        room = Blob(cells)
        rooms.append(room)
    yield rooms

def place_rooms(rooms):
  if not rooms:
    yield True
  rooms.sort(key=lambda r: -r.get_area())
  graph = FloorGraph(nodes=[rooms[0]])
  total_blob = rooms[0]
  total_connectors = []
  for i, room in enumerate(rooms[1:]):
    total_hitbox = total_blob.hitbox
    ticks = get_ticks()
    iters = 0
    iters_max = 0
    origin = room.origin
    connectors = room.connectors
    valid_edges = {}
    shuffle(graph.nodes)
    for neighbor in graph.nodes:
      if neighbor.degree and graph.degree(neighbor) >= neighbor.degree:
        continue
      combinations = [*product(connectors, neighbor.connectors)]
      origins = [subtract_vector(c2, subtract_vector(c1, origin)) for c1, c2 in combinations]
      shuffle(combinations)
      iters_max += len(combinations)
      for o in origins:
        iters += 1
        room.origin = o
        if not (room.hitbox & total_hitbox):
          neighbor_connectors = { n: cs for n, cs in [(n, [c for c in set(n.connectors) & set(room.connectors) if not next((t for t in total_connectors if t in neighborhood(c, inclusive=True, diagonals=True)), None)]) for n in graph.nodes] if cs }
          if neighbor_connectors:
            valid_edges[o] = neighbor_connectors
            if len(neighbor_connectors) >= 2 or len(graph.nodes) < 3:
              for neighbor, connectors in neighbor_connectors.items():
                graph.add(room)
                graph.connect(room, neighbor, *connectors)
        if room in graph.nodes or (get_ticks() - ticks) > 1000 / FPS * 2:
          ticks = get_ticks()
          if room not in graph.nodes:
            yield None, f"Placing room {i + 2} of {len(rooms)} ({iters}/{iters_max})"
          else:
            yield graph, f"Placed room {i + 2} of {len(rooms)} at {room.origin} after {iters} iteration(s)"
            break
      if room in graph.nodes:
        break

    if room not in graph.nodes and valid_edges:
      origin, neighbor_connectors = [*valid_edges.items()][0]
      neighbor, connectors = [*neighbor_connectors.items()][0]
      room.origin = origin
      graph.add(room)
      graph.connect(room, neighbor, *connectors)
      print("Using cached edge")

    if room in graph.nodes:
      total_blob = Blob(total_blob.cells + room.cells)
      total_connectors += connectors
      yield graph, f"Placed room {i + 2} of {len(graph.nodes)} at {room.origin}"
    else:
      yield False, "Failed to place rooms"

  yield graph, ""

def gen_tree(graph, start=None):
  tree = FloorGraph()
  if start is None:
    start = choice(graph.nodes)
  stack = [start]
  while stack:
    node = stack[0]
    tree.add(node)
    neighbors = [n for n in graph.neighbors(node) if tree.degree(n) == 0]
    if neighbors:
      neighbor = choice(neighbors)
      connectors = graph.connectors(node, neighbor)
      connector = choice(connectors)
      tree.connect(node, neighbor, connector)
      stack.insert(0, neighbor)
    else:
      stack.pop(0)
  return tree

def gen_loop(tree, graph, node=None, min_distance=3):
  if not node:
    ends = tree.ends()
    if not ends:
      return False
    node = choice(ends)
  neighbors = [n for n in graph.neighbors(node) if (
    n not in tree.neighbors(node)
    and tree.distance(node, n) >= min_distance
  )]
  if neighbors:
    neighbor = choice(neighbors)
    connectors = graph.connectors(node, neighbor)
    connector = choice(connectors)
    tree.connect(node, neighbor, connector)
    return True
  else:
    return False

def gen_loops(tree, graph):
  loops = 0
  for node in tree.nodes:
    if tree.degree(node) <= 2:
      loops |= gen_loop(tree, graph, node, min_distance=3)
      break
  if not loops:
    for node in tree.nodes:
      if tree.degree(node) <= 2 and gen_loop(tree, graph, node, min_distance=2):
        break


def gen_floor(
  rooms=[],
  enemies=[Eyeball, Mushroom, Ghost, Mummy],
  items=[Potion, Cheese, Bread, Fish, Antidote, MusicBox, LovePotion, Booze],
  seed=None
):
  seed = seed if seed is not None else getrandbits(32)
  random.seed(seed)

  lkg = None
  while lkg is None:
    stage = None

    features = rooms
    rooms = [Blob(data=r) for r in features]
    max_rooms = 4 # randint(MIN_ROOM_COUNT, MAX_ROOM_COUNT)
    rooms_gen = gen_rooms(init=rooms, count=max_rooms)
    while len(rooms) < max_rooms:
      rooms = next(rooms_gen)
      if len(rooms) == max_rooms:
        yield None, f"Room generation succeeded"
      else:
        yield None, f"Generating room {len(rooms) + 1} of {max_rooms}"

    # place rooms
    graph, message = {}, "*"
    room_count = 0
    place_gen = place_rooms(rooms)
    while graph is not False and message:
      graph, message = next(place_gen)
      if not graph:
        yield None, message
      elif graph.order() != room_count:
        room_count = graph.order()
        stage, _ = manifest_stage(graph.nodes, dry=True) # possibly a perf bottleneck - use debug flag to toggle (scope to config or generator?)
        stage.seed = seed
        yield stage, message

    # manifest_stage(rooms) -> stage
    stage, stage_offset = manifest_stage(rooms)
    stage.seed = seed

    if graph is False:
      yield stage, message
      continue

    tree = gen_tree(graph)
    gen_loops(tree, graph)

    # DrawConnectors(stage, stage_offset, tree)
    connected = True
    door_paths = set()
    for i, ((room1, room2), connectors) in enumerate(tree.connections()):
      connectors = [add_vector(c, stage_offset) for c in connectors]
      if len(connectors) > 1:
        connectors.sort(key=lambda c: (
          manhattan(c, room1.find_closest_cell(c))
          + manhattan(c, room2.find_closest_cell(c))
        ))

      for j, connector in enumerate(connectors):
        is_edge_usable = lambda e, room: (
          next((e for e in stage.get_elems_at(e) if isinstance(e, Door)), None)
          or (
            not next((n for n in neighborhood(e) if next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)), None)
            and len([n for n in neighborhood(e) if stage.get_tile_at(n) is Stage.WALL]) == 3
            and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is Stage.WALL]) in (5, 6, 7)
            # and not next((c for c in [c for r in [r for r in rooms if r is not room] for c in r.outline] if is_adjacent(c, e)), None)
            and not e in stage.get_border()
          )
        )

        prev_edges = [e for e in room1.edges if is_edge_usable(e, room=room1)]
        if not prev_edges:
          yield stage, f"Failed to find usable edges for room {i + 1}"
          connected = False
          break
        prev_edges.sort(key=lambda e: manhattan(e, connector))

        room_edges = [e for e in room2.edges if is_edge_usable(e, room=room2)]
        if not room_edges:
          yield stage, f"Failed to find usable edges for room {i + 2}"
          connected = False
          break
        room_edges.sort(key=lambda e: manhattan(e, connector))

        door_path = None
        room_outlines = set([c for r in rooms for c in r.outline])
        path_blacklist = room_outlines | door_paths | set(stage.get_border())
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

          if {door1_start, door2_start} & path_blacklist:
            continue

          neighborhood_overlap = set(neighborhood(door1_start)) & set(neighborhood(door2_start))
          if neighborhood_overlap:
            door_neighbor = add_vector(door1_start, door1_delta)
            if door_neighbor not in neighborhood(door2_start):
              door_neighbor = add_vector(door2_start, door2_delta)
            if door_neighbor not in neighborhood(door1_start):
              door_neighbor = [*neighborhood_overlap][0]
            door_path = [door1_start, door_neighbor, door2_start]
            break

          door_path = gen_path(start=door1_start, goal=door2_start, predicate=lambda c: c not in path_blacklist, straight=True)
          if door_path:
            break

        if door_path:
          break
        else:
          stage.spawn_elem_at(connector, Eyeball())
          yield stage, f"Skipping unusable connector {connector} - {len(connectors) - j - 1} left"

      if not door_path:
        connected = False
        yield stage, f"Failed to path between rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1}"
        break

      # TODO: cache this path and only draw after all paths are cached (fail tolerance)
      # need to be able to trace conflicting cells back to the connectors that made them(?)
      door_path = [door1] + door_path + [door2]
      stage.spawn_elem_at(door1, Door())
      stage.spawn_elem_at(door2, Door())
      for cell in door_path:
        stage.set_tile_at(cell, Stage.HALLWAY)
        door_paths.update(neighborhood(cell, inclusive=True, diagonals=True))

      tree.reconnect(room1, room2, door1, door2)
      yield stage, f"Connected rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1} at {connector}"

    if not connected:
      continue

    rooms.sort(key=lambda r: r.get_area())
    feature_rooms = [r for r in rooms if r.data in features]
    plain_rooms = [r for r in rooms if r not in feature_rooms]
    empty_rooms = plain_rooms.copy()

    for room in feature_rooms:
      if "on_place" in room.data.events:
        on_place = resolve_event(room.data.events["on_place"])
        on_place and on_place(stage, room)

    # SpawnEntrance(stage) -> room
    entry_room = None
    for room in empty_rooms:
      entrances = [c for c in room.cells if not next((n for n in neighborhood(c, inclusive=True, diagonals=True) if not stage.is_cell_empty(n)), None)]
      if entrances:
        stage.entrance = choice(entrances)
        stage.set_tile_at(stage.entrance, Stage.STAIRS_DOWN)
        empty_rooms.remove(room)
        entry_room = room
        yield stage, f"Spawned entrance at {stage.entrance}"
        break
    else:
      yield stage, "Failed to spawn entrance"

    secrets = [e for e in tree.ends() if e in empty_rooms if e.get_area() <= 50]
    for secret in secrets:
      neighbor = tree.neighbors(secret)[0]
      doors = tree.connectors(secret, neighbor)
      doorways = neighbor.get_doorways(stage)
      doorway = next((d for d in doorways if d in doors), None)
      door = next((e for e in stage.get_elems_at(doorway) if isinstance(e, Door)), None)
      stage.remove_elem(door)
      stage.spawn_elem_at(doorway, SecretDoor())

      neighbor = next((n for n in neighborhood(doorway) if stage.get_tile_at(n) is Stage.FLOOR), None)
      if neighbor:
        neighbor_x, neighbor_y = neighbor
        door_delta = subtract_vector(neighbor, doorway)
        door_xdelta, door_ydelta = door_delta
        if (door_delta
        and stage.is_cell_empty((neighbor_x - door_ydelta, neighbor_y - door_xdelta))
        and stage.is_cell_empty((neighbor_x + door_ydelta, neighbor_y + door_xdelta))
        ):
          stage.spawn_elem_at(neighbor, ArrowTrap(facing=door_delta, delay=inf, static=False))

      print(f"Spawned secret with area {secret.get_area()}")
      empty_rooms.remove(secret)

    # draw room terrain
    for room in plain_rooms:
      gen_terrain(stage, room, tree)

    # populate rooms
    for i, room in enumerate(rooms):
      if room in secrets:
        stage.spawn_elem_at(room.get_center(), Chest(Elixir))
        item_count = min(8, room.get_area() // 20)
        room_items = [Vase(choice(ALL_ITEMS)) for _ in range(item_count)]
      else:
        item_count = min(3, room.get_area() // 20)
        room_items = [Vase(choice(items)) for _ in range(item_count)]
      gen_elems(stage, room, elems=room_items)

    for i, room in enumerate(empty_rooms):
      enemies_spawned = gen_elems(stage, room,
        elems=[choice(enemies)(
          ailment=("sleep" if randint(1, 3) == 1 else None)
        ) for _ in range(min(5, room.get_area() // 20))]
      )

    stage.rooms = rooms
    lkg = stage
    break

  yield stage, ""
