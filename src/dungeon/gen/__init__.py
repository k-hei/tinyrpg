from math import inf
from itertools import product
import random
from random import randint, getrandbits, choice, shuffle
from pygame.time import get_ticks
from lib.cell import neighborhood, manhattan, add as add_vector, subtract as subtract_vector
from lib.graph import Graph
from debug import bench
from config import FPS

from contexts.explore.stage import Stage
import tiles.default as tileset
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from contexts.explore.roomdata import load_rooms
from dungeon.gen.terrain import gen_terrain
from dungeon.gen.elems import gen_elems
from dungeon.gen.blob import gen_blob
from dungeon.gen.path import gen_path
from contexts.explore.manifest import manifest_rooms
from dungeon.gen.floorgraph import FloorGraph
from dungeon.props.door import Door as GenericDoor
from dungeon.props.raretreasuredoor import RareTreasureDoor
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.vase import Vase
from dungeon.props.chest import Chest
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.table import Table

from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy

from items.sets import NORMAL_ITEMS, SPECIAL_ITEMS
from items.dungeon.key import Key

from resolve.elem import resolve_elem

load_rooms()

MIN_ROOM_COUNT = 7
MAX_ROOM_COUNT = MIN_ROOM_COUNT + 0

def gen_rooms(count, init=None):
  rooms = init or []
  while len(rooms) < count:
    cells = (len(rooms) > count // 3
      and gen_blob(min_area=80, max_area=100)
      or gen_blob(min_area=150, max_area=240)
    )
    room = Room(cells)
    rooms.append(room)
  return rooms

def place_rooms(rooms, force_connect=False):
  if not rooms:
    yield True
  graph = FloorGraph(nodes=[rooms[0]])
  total_blob = rooms[0]
  total_connectors = []
  for i, room in enumerate(rooms[1:]):
    if room.degree and graph.degree(room) >= room.degree:
      continue
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
      origins = [
        subtract_vector(c2, subtract_vector(c1, origin))
          for c1, c2 in product(connectors, neighbor.connectors)
            if (c1 in room.connector_deltas
            and c2 in neighbor.connector_deltas
            and room.connector_deltas[c1] != neighbor.connector_deltas[c2])
      ]
      shuffle(origins)
      iters_max += len(origins)
      for o in origins:
        iters += 1
        room.origin = o
        if not (room.hitbox & total_hitbox):
          neighbor_connectors = {
            n: cs for n, cs in [
              (n, [
                c for c in set(n.connectors) & set(room.connectors) if (
                  not next((t for t in total_connectors if t in neighborhood(c, inclusive=True, diagonals=True)), None)
                )
              ]) for n in graph.nodes
                if not n.degree or graph.degree(n) < n.degree
            ] if cs
          }
          if neighbor_connectors:
            valid_edges[o] = neighbor_connectors
            if len(neighbor_connectors) >= 2 or len(graph.nodes) < 2:
              for neighbor, connectors in neighbor_connectors.items():
                graph.add(room)
                graph.connect(room, neighbor, *connectors)
        if room in graph.nodes or (get_ticks() - ticks) > 1000 / FPS:
          ticks = get_ticks()
          if room not in graph.nodes:
            yield None, f"Placing room {i + 2} of {len(rooms)} ({iters}/{iters_max})"
          else:
            break
      if room in graph.nodes:
        break

    if room not in graph.nodes and valid_edges and not (force_connect and (room.degree == 0 or room.degree >= 3)):
      origin, neighbor_connectors = [*valid_edges.items()][0]
      neighbor, connectors = [*neighbor_connectors.items()][0]
      room.origin = origin
      graph.add(room)
      graph.connect(room, neighbor, *connectors)

    if room in graph.nodes:
      total_blob = Room(total_blob.cells + room.cells)
      total_connectors += connectors
      yield graph, f"Placed room {i + 2} of {len(rooms)} at {room.origin} after {iters} iteration(s)"
    else:
      yield False, "Failed to place rooms"

  yield graph, ""

def find_chunks(graph):
  chunks = []
  for node in graph.nodes:
    if (next((n for c in chunks for n in c.nodes if n is node), None)
    or next(((n1, n2) for c in chunks for n1, n2 in c.edges if n1 is node or n2 is node), None)):
      continue
    chunk = Graph(nodes=[node])
    stack = [node]
    while stack:
      node = stack.pop()
      for neighbor in graph.neighbors(node):
        if (node, neighbor) in chunk.edges or (neighbor, node) in chunk.edges:
          continue
        chunk.edges.append((node, neighbor))
        if neighbor in chunk.nodes:
          continue
        chunk.nodes.append(neighbor)
        stack.append(neighbor)
    chunks.append(chunk)
  return chunks

def gen_place(graph, parent, child, sibling=None):
  graph_blob = Room(cells=[c for n in graph.nodes for c in n.cells])
  used_connectors = [c for cs in graph.conns.values() for c in cs]
  init_origin = child.origin
  origins = [
    subtract_vector(c1, subtract_vector(c2, child.origin))
      for c1, c2 in product(parent.connectors, child.connectors)
        if (c1 in parent.connector_deltas
        and c2 in child.connector_deltas
        and parent.connector_deltas[c1] != child.connector_deltas[c2])
  ]
  sibling and print("INFO: Connecting with sibling")
  shuffle(origins)
  for origin in origins:
    child.origin = origin
    if child.hitbox & graph_blob.hitbox:
      continue
    if sibling:
      neighbor_connectors = {
        n: cs for n, cs in [
          (n, [
            c for c in set(n.connectors) & set(child.connectors)
              if not next((n for n in neighborhood(c, inclusive=True, diagonals=True) if n in used_connectors), None)
          ]) for n in graph.nodes
            if not n.degree or graph.degree(n) < n.degree
        ] if cs
      }
      if neighbor_connectors and (len(neighbor_connectors) >= 2 or len(graph.nodes) < 2):
        for neighbor, connectors in neighbor_connectors.items():
          graph.add(child)
          graph.connect(child, neighbor, *connectors)
        return [c for cs in neighbor_connectors.values() for c in cs]
    else:
      connectors = list(set(parent.connectors) & set(child.connectors))
      connector = next((c for c in connectors if not next((n for n in neighborhood(c, diagonals=True, inclusive=True) if n in used_connectors), None)), None)
      if not connector:
        continue
      child not in graph.nodes and graph.add(child)
      graph.connect(parent, child, connector)
      return connector
  child.origin = init_origin
  return None

def gen_joint_connect(feature_graph):
  start = feature_graph.edges[0][0] if feature_graph.edges else sorted(feature_graph.nodes, key=feature_graph.degree)[-1]
  graph = FloorGraph(nodes=[start])
  stack = [start]
  while stack:
    node = stack.pop(0)
    for neighbor in feature_graph.neighbors(node):
      neighbor_neighbors = feature_graph.neighbors(neighbor)
      siblings = set(neighbor_neighbors) & set(graph.nodes)
      if neighbor in graph.nodes:
        continue
      sibling = next((n for n in neighbor_neighbors if n is not node), None) if len(siblings) >= 2 else None
      connector = gen_place(graph, parent=node, child=neighbor, sibling=sibling)
      if connector:
        stack.append(neighbor)
        yield graph
      else:
        print("Connection failed", node.data, neighbor.data)
        yield False
        return

def gen_connect(feature_graph):
  if len(feature_graph.edges) >= len(feature_graph.nodes):
    print(f"Joint connect with {len(feature_graph.nodes)} nodes")
    connect_gen = gen_joint_connect(feature_graph)
    floor_graph = None
    while floor_graph is not False:
      try:
        floor_graph = next(connect_gen)
        yield floor_graph
      except StopIteration:
        break
    return

  start = feature_graph.edges[0][0] if feature_graph.edges else sorted(feature_graph.nodes, key=feature_graph.degree)[-1]
  floor_graph = FloorGraph(nodes=[start])
  if feature_graph.order() == 1:
    yield floor_graph
    return

  stack = [start]
  while stack:
    node = stack.pop(0)
    for neighbor in feature_graph.neighbors(node):
      if (node, neighbor) in floor_graph.edges or (neighbor, node) in floor_graph.edges:
        continue
      connector = gen_place(graph=floor_graph, parent=node, child=neighbor)
      if connector:
        stack.append(neighbor)
        yield floor_graph
      else:
        print("Connection failed", node.data, neighbor.data)
        yield False
        return

def gen_merge(graph1, graph2, indices=None):
  blob1 = Room(cells=[c for n in graph1.nodes for c in n.cells])
  blob2 = Room(cells=[c for n in graph2.nodes for c in n.cells])
  graph1_connections = {c: n for n in graph1.nodes for c in n.connectors if n.degree == 0 or graph1.degree(n) < n.degree}
  graph2_connections = {c: n for n in graph2.nodes for c in n.connectors if n.degree == 0 or graph2.degree(n) < n.degree}
  init_origin = blob2.origin
  origins = [
    (subtract_vector(c1, subtract_vector(c2, blob2.origin)), n1, n2)
      for (c1, n1), (c2, n2) in product(graph1_connections.items(), graph2_connections.items())
        if (c1 in n1.connector_deltas
        and c2 in n2.connector_deltas
        and n1.connector_deltas[c1] != n2.connector_deltas[c2])
  ]

  shuffle(origins)

  index_ids = f"{indices[0] + 1} and {indices[1] + 1}" if indices else ""

  bench("Merging graphs")
  time_start = get_ticks()
  for i, (origin, room1, room2) in enumerate(origins):
    delta = subtract_vector(origin, init_origin)
    blob2.origin = add_vector(init_origin, delta)
    if blob1.hitbox & blob2.hitbox:
      if get_ticks() - time_start > 1000 / FPS:
        time_start = get_ticks()
        yield None, (index_ids
          and f"Merging graphs {index_ids} ({i + 1}/{len(origins)})"
          or f"Testing graph merge origin {i + 1}/{len(origins)}")
      continue
    for node in graph2.nodes:
      node.origin = add_vector(node.origin, delta)
    connectors = list(set(room1.connectors) & set(room2.connectors))
    used_connectors = [c for cs in graph1.conns.values() for c in cs]
    connector = next((c for c in connectors if not next((n for n in neighborhood(c, diagonals=True, inclusive=True) if n in used_connectors), None)), None)
    if not connector:
      continue
    graph1.connect(room1, room2, connector)
    for edge in graph2.edges:
      del graph2.conns[edge]
      n1, n2 = edge
      graph2.conns[edge] = tuple(set(n1.connectors) & set(n2.connectors))
    graph1.merge(graph2)
    time_delta = bench("Merging graphs", print_threshold=inf)
    yield graph1, "Successfully merged graphs" + (f" {index_ids}" if index_ids else "") + f" in {time_delta}ms"
  else:
    yield False, "Failed to merge graphs" + (f" {index_ids}" if index_ids else "")

def gen_assemble(graphs):
  is_graph_dead_end = lambda g: not next((n for n in g.nodes if n.degree != 1), None)
  original_graphs = sorted(graphs, key=lambda g: g.order() + random.random() / 2 + (-100 if is_graph_dead_end(g) else 0), reverse=True)
  graphs = original_graphs.copy()
  while len(graphs) > 1:
    g1 = graphs[0]
    result = None
    for g2 in graphs[1:]:
      merge_gen = gen_merge(g1, g2, indices=(original_graphs.index(g1), original_graphs.index(g2)))
      while result is None:
        result, message = next(merge_gen)
        yield [g for g in graphs if g is not g1], message
      if result is False:
        yield False, "Failed to assemble graphs"
        yield g1
      break
    if result is False:
      break
    graphs = [g for g in graphs if g is not g2]
    yield [g for g in graphs if g is not g1], ""
  yield g1

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
        loops += 1
        break

  if not loops:
    for node in tree.nodes:
      if gen_loop(tree, graph, node, min_distance=2):
        loops += 1
        break

  return loops

def gen_floor(
  features=[],
  enemies=[Eyeball, Mushroom], # [Eyeball, Mushroom, Ghost, Mummy],
  items=NORMAL_ITEMS,
  extra_room_count=0,
  seed=None,
  debug=False
):
  seed = seed if seed is not None else getrandbits(32)
  random.seed(seed)

  lkg = None
  while lkg is None:
    stage = None

    feature_graph = features() if callable(features) else features
    if not isinstance(feature_graph, Graph):
      feature_graph = Graph(nodes=feature_graph, edges=[])

    # resolve feature graph chunks
    feature_chunks = find_chunks(feature_graph)
    yield None, f"Found {len(feature_chunks)} feature chunk(s)"

    # assemble feature graph chunks
    floor_chunks = []
    for i, feature_chunk in enumerate(feature_chunks):
      chunk_id = f"{i + 1}/{len(feature_chunks)}"
      connect_gen = gen_connect(feature_chunk)
      floor_chunk = None
      stage = None
      while floor_chunk is not False:
        try:
          floor_chunk = next(connect_gen)
        except StopIteration:
          break
        if floor_chunk:
          stage, stage_offset = manifest_rooms(floor_chunk.nodes, dry=True, seed=seed)
      if not floor_chunk:
        if stage:
          for connector in stage.rooms[-1].connectors:
            connector = add_vector(connector, stage_offset)
            stage.spawn_elem_at(connector, Eyeball())
        yield stage, f"Failed to assemble chunk {chunk_id} ({len(feature_chunk.nodes)} nodes)"
        break
      floor_chunks.append(floor_chunk)
      yield None, f"Assembled chunk {chunk_id}"

    if len(floor_chunks) != len(feature_chunks):
      continue

    # generate extra rooms
    extra_rooms = []
    while len(extra_rooms) < extra_room_count:
      room_cells = gen_blob(min_area=80, max_area=120)
      room = Room(cells=room_cells)
      extra_rooms.append(room)
      if len(extra_rooms) < extra_room_count:
        yield None, f"Generating room {len(extra_rooms) + 1} of {extra_room_count}"
      else:
        yield None, f"Room generation succeeded"

    # assemble extra rooms
    if extra_rooms:
      place_gen = place_rooms(rooms=extra_rooms)
      extra_graph, message = None, "*"
      while extra_graph is not False and message:
        try:
          extra_graph, message = next(place_gen)
          if extra_graph:
            stage = manifest_rooms(extra_graph.nodes, dry=True, seed=seed)[0]
          yield stage, message # f"Placing room {len(extra_graph.nodes)} of {len(extra_rooms)}"
        except StopIteration:
          break
      tree = gen_tree(extra_graph)
      loops = gen_loops(tree, extra_graph)
      floor_chunks.insert(0, tree)
      if not loops and extra_room_count >= 3:
        yield manifest_rooms(extra_graph.nodes, dry=True, seed=seed)[0], "Failed to create loops"
        continue

    # assemble graphs
    if len(floor_chunks) > 1:
      graphs_left, message = floor_chunks, ""
      assemble_gen = gen_assemble(floor_chunks)
      while graphs_left:
        graph_id = len(floor_chunks) - len(graphs_left) if len(graphs_left) != len(floor_chunks) else 1
        yield None, message
        graphs_left, message = next(assemble_gen)

      if graphs_left is False:
        graph = next(assemble_gen)
        stage = manifest_rooms(graph.nodes, seed=seed)[0] if debug else None
        if stage and next((x for x in stage.size if x > 100), None):
          stage = None # HACK: need to figure out why failures generate massive stages
        yield stage, "Failed to assemble graphs"
        continue
      graph = next(assemble_gen)
    else:
      graph = floor_chunks[0]

    rooms = graph.nodes
    stage, stage_offset = manifest_rooms(rooms)
    stage.seed = seed

    # DrawConnectors(stage, stage_offset, tree)
    connected = True
    key_count = 0
    door_paths = set()
    for i, ((room1, room2), connectors) in enumerate(graph.connections()):
      bench("Connect rooms", reset=True)
      connectors = [add_vector(c, stage_offset) for c in connectors]
      if len(connectors) > 1:
        connectors.sort(key=lambda c: (
          manhattan(c, room1.find_closest_cell(c))
          + manhattan(c, room2.find_closest_cell(c))
        ))

      door_path = None

      for j, connector in enumerate(connectors):
        # stage.spawn_elem_at(connector, Eyeball(faction="ally"))
        if not stage.contains(connector):
          print(f"WARNING: Connector {connector} out of bounds")
        is_edge_usable = lambda e, room: (
          next((e for e in stage.get_elems_at(e) if isinstance(e, GenericDoor)), None)
          or (
            not next((n for n in neighborhood(e) if next((e for e in stage.get_elems_at(n) if isinstance(e, GenericDoor)), None)), None)
            and len([n for n in neighborhood(e) if stage.get_tile_at(n) is tileset.Wall]) == 3
            and len([n for n in neighborhood(e, diagonals=True) if stage.get_tile_at(n) is tileset.Wall]) in (5, 6, 7)
            # and not next((c for c in [c for r in [r for r in rooms if r is not room] for c in r.outline] if is_adjacent(c, e)), None)
            and not e in stage.border
          )
        )

        prev_edges = [e for e in room1.edges if is_edge_usable(e, room=room1)]
        if not prev_edges:
          for e in room1.edges:
            stage.spawn_elem_at(e, Eyeball(faction="ally"))
          yield stage, f"Failed to find usable edges for room {i + 1}"
          connected = False
          break
        prev_edges.sort(key=lambda e: manhattan(e, connector))

        room_edges = [e for e in room2.edges if is_edge_usable(e, room=room2)]
        if not room_edges:
          for e in room2.edges:
            stage.spawn_elem_at(e, Eyeball(faction="ally"))
          yield stage, f"Failed to find usable edges for room {i + 2}"
          connected = False
          break
        room_edges.sort(key=lambda e: manhattan(e, connector))

        door_path = None
        room_outlines = set([c for r in rooms for c in r.outline])
        path_blacklist = room_outlines | door_paths | set(stage.border)
        for door1_cell, door2_cell in product(prev_edges, room_edges):
          if (door1_cell in prev_edges and door2_cell in prev_edges
          or door1_cell in room_edges and door2_cell in room_edges):
            continue

          door1_neighbor = next((n for n in neighborhood(door1_cell) if n in room1.cells), None)
          door1_delta = subtract_vector(door1_cell, door1_neighbor)
          door1_start = add_vector(door1_cell, door1_delta)

          door2_neighbor = next((n for n in neighborhood(door2_cell) if n in room2.cells), None)
          door2_delta = subtract_vector(door2_cell, door2_neighbor)
          door2_start = add_vector(door2_cell, door2_delta)

          if {door1_start, door2_start} & path_blacklist:
            continue

          neighborhood_overlap = set(neighborhood(door1_start)) & set(neighborhood(door2_start))
          if neighborhood_overlap:
            door_neighbor = add_vector(door1_start, door1_delta)
            if door_neighbor not in neighborhood(door2_start):
              door_neighbor = add_vector(door2_start, door2_delta)
            if door_neighbor not in neighborhood(door1_start):
              door_neighbor = [*neighborhood_overlap][0]
            if door_neighbor in path_blacklist:
              continue
            door_path = [door1_start, door_neighbor, door2_start]
            break

          door_path = gen_path(start=door1_start, goal=door2_start, delta=door1_delta, predicate=lambda c: c not in path_blacklist)
          if door_path:
            break

        if door_path:
          break
        else:
          stage.spawn_elem_at(connector, Mummy())
          yield stage, f"Skipping unusable connector {connector} - {len(connectors) - j - 1} left"

      if not door_path:
        connected = False
        yield stage, f"Failed to path between rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1}"
        break

      # TODO: cache this path and only draw after all paths are cached (fail tolerance)
      # need to be able to trace conflicting cells back to the connectors that made them(?)
      door_path = [door1_cell] + door_path + [door2_cell]

      Door1 = resolve_elem(room1.data.doors) if room1.data else GenericDoor
      Door2 = resolve_elem(room2.data.doors) if room2.data else GenericDoor
      Door = (Door1 if Door1 is not GenericDoor
        else Door2 if Door2 is not GenericDoor
        else GenericDoor)

      exit_room = (
        room1 if next((c for c in room1.cells if stage.get_tile_at(c) is tileset.Exit), None)
        else room2 if next((c for c in room2.cells if stage.get_tile_at(c) is tileset.Exit), None)
        else None
      )
      if exit_room:
        entry_room = next((r for r in rooms for c in r.cells if stage.get_tile_at(c) is tileset.Entrance), None)
        if entry_room and graph.distance(entry_room, exit_room) == 2:
          Door = RareTreasureDoor

      if Door is RareTreasureDoor:
        key_count += 1

      door1, door2 = Door(), Door()
      stage.spawn_elem_at(door1_cell, door1)
      stage.spawn_elem_at(door2_cell, door2)
      for cell in door_path:
        stage.set_tile_at(cell, tileset.Hallway)
        door_paths.update(neighborhood(cell, inclusive=True, diagonals=True))

      graph.reconnect(room1, room2, door1, door2)
      time_delta = bench("Connect rooms", print_threshold=inf)
      yield stage, f"Connected rooms {rooms.index(room1) + 1} and {rooms.index(room2) + 1} at {connector} in {time_delta}ms"

    if not connected:
      continue

    rooms.sort(key=lambda r: r.get_area())
    feature_rooms = feature_graph.nodes
    plain_rooms = [r for r in rooms if not r.data or r.data.terrain]
    empty_rooms = [r for r in rooms if r not in feature_rooms or not r.data.tiles]

    secrets = [e for e in rooms if (
      e.data and e.data.secret
      or e in empty_rooms and graph.degree(e) == 1 and (
        e.get_area() <= 60
        and not (e.data and e.data.doors != "Door")
        and not next((n for n in graph.neighbors(e) if n.data and n.data.doors != "Door"), None)
      )
    )]
    for secret in secrets:
      neighbor = graph.neighbors(secret)[0]
      for door in graph.connectors(secret, neighbor):
        doorway = door.cell
        stage.remove_elem(door)
        stage.spawn_elem_at(doorway, SecretDoor())

      neighbor = next((n for n in neighborhood(doorway) if stage.get_tile_at(n) is tileset.Floor), None)
      if neighbor:
        neighbor_x, neighbor_y = neighbor
        door_delta = subtract_vector(neighbor, doorway)
        door_xdelta, door_ydelta = door_delta
        if (door_delta
        and door_delta != (0, -1)
        and stage.is_cell_empty((neighbor_x - door_ydelta, neighbor_y - door_xdelta))
        and stage.is_cell_empty((neighbor_x + door_ydelta, neighbor_y + door_xdelta))
        and stage.get_tile_at((neighbor_x + door_xdelta * 2, neighbor_y + door_ydelta * 2)) is not tileset.Wall
        and randint(0, 1)
        ):
          stage.spawn_elem_at(neighbor, ArrowTrap(facing=door_delta, delay=inf, static=False))

      print(f"Spawned secret with area {secret.get_area()} at {doorway}")
      if secret in empty_rooms:
        empty_rooms.remove(secret)

    # draw room terrain
    island_rooms = {}
    for room in plain_rooms:
      island_centers = gen_terrain(stage, room, graph)
      if island_centers:
        for cell in island_centers:
          island_rooms[cell] = room
      else:
        break

    if island_rooms and not island_centers:
      yield stage, "Failed to draw terrain"
      continue

    key_containers = [
      e for r in rooms
        for c in r.cells
          for e in stage.get_elems_at(c)
            if "contents" in dir(e) and e.contents is Key
    ]
    key_count = max(0, key_count - len(key_containers))

    if key_count:
      island_centers = [*island_rooms.keys()]
      if len(island_centers) < key_count:
        yield stage, "Failed to spawn keys"
        continue

      shuffle(island_centers)
      island_centers.sort(key=lambda c: graph.degree(island_rooms[c]))
      key_cells = island_centers[:key_count]
      for cell in key_cells:
        stage.spawn_elem_at(cell, Chest(Key))

    # populate rooms
    for room in rooms:
      if not (room.data and room.data.tiles) and randint(0, 1):
        table_length = randint(2, 3)
        find_table_cells = lambda c: (
          table_length == 2 and [c, add_vector(c, (1, 0))]
          or table_length == 3 and [c, add_vector(c, (1, 0)), add_vector(c, (2, 0))]
        )
        table_cell = next((c for c in sorted(room.cells, key=lambda _: random.random()) if (
          not next((n for t in find_table_cells(c) for n in neighborhood(t, diagonals=True) if (
            not stage.is_cell_empty(n) or not issubclass(stage.get_tile_at(n), tileset.Floor)
          )), None)
        )), None)
        if table_cell:
          stage.spawn_elem_at(table_cell, Table(length=table_length))

      if room.data and not room.data.items:
        continue

      if room.data and type(room.data.items) is list:
        room_items = [Vase(contents=i) for i in room.data.items]
      elif room in secrets:
        item_count = min(8, room.get_area() // 16)
        room_items = [Vase(contents=choice(SPECIAL_ITEMS)) for _ in range(item_count)]
      else:
        item_count = max(1, min(3, room.get_area() // 24))
        room_items = [Vase(contents=choice(items)) for _ in range(item_count)]
      vases_spawned = gen_elems(stage, room, elems=room_items)

    for i, room in enumerate(rooms):
      if room.data and not room.data.enemies:
        continue
      if room.data and type(room.data.enemies) is list:
        elems = room.data.enemies
        for enemy in elems:
          if randint(1, 3) == 1:
            enemy.inflict_ailment("sleep")
      if not room.data or type(room.data.enemies) is bool:
        elems = [choice(enemies)(
          ailment=("sleep" if randint(1, 3) == 1 else None)
        ) for _ in range(min(5, room.get_area() // 16))]
      enemies_spawned = gen_elems(stage, room, elems)

    for room in rooms:
      room.on_place(stage)

    if not stage.entrance:
      stage.entrance = next((c for c in stage.cells if issubclass(stage.get_tile_at(c), tileset.Entrance)), None)

    if not stage.entrance:
      yield stage, "Failed to spawn entrance"
      continue

    stage.rooms = rooms
    lkg = stage
    break

  yield stage, ""
