import pygame
import random
from random import randint, randrange, choice, choices, getrandbits
from lib.cell import is_odd, add, is_adjacent, manhattan

import config
from config import ROOM_WIDTHS, ROOM_HEIGHTS

from dungeon.stage import Stage
from dungeon.gen.floorgraph import FloorGraph
from dungeon.features.maze import Maze
from dungeon.features.room import Room
from dungeon.features.exitroom import ExitRoom
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.arenaroom import ArenaRoom
from dungeon.features.raretreasureroom import RareTreasureRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.coffinroom import CoffinRoom
from dungeon.features.pitroom import PitRoom
from dungeon.features.elevroom import ElevRoom
from dungeon.features.itemroom import ItemRoom

from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.actors.eye import Eye
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.soldier import Soldier
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import Npc
from dungeon.actors.genie import Genie

from dungeon.props.chest import Chest
from dungeon.props.bag import Bag
from dungeon.props.door import Door
from dungeon.props.battledoor import BattleDoor
from dungeon.props.treasuredoor import TreasureDoor
from dungeon.props.coffin import Coffin
from dungeon.props.soul import Soul
from dungeon.props.pushblock import PushBlock
from dungeon.props.pushtile import PushTile

from items.hp.potion import Potion
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.sp.cheese import Cheese
from items.sp.bread import Bread
from items.sp.fish import Fish
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.dungeon.key import Key
from items.ailment.antidote import Antidote
from items.materials.angeltears import AngelTears

from skills.support.counter import Counter

class Floor:
  def __init__(floor, size):
    floor.slots = Floor.gen_slots(size)
    floor.stage = Stage(size)
    floor.stage.fill(Stage.WALL)
    floor.graph = FloorGraph()
    floor.tree = FloorGraph()

  def mark(floor, feature):
    for slot in feature.get_slots():
      if slot in floor.slots:
        floor.slots.remove(slot)
    floor.graph.add(feature)

  def gen_slots(size):
    slots = []
    width, height = size
    for y in range(height):
      for x in range(width):
        if x % 2 == 1 and y % 3 == 1:
          slots.append((x, y))
    return slots

  def gen_rooms(floor):
    rooms = []
    attempts = config.MAX_ROOM_FAILS
    while attempts:
      room = floor.gen_room()
      if floor.gen_place(room):
        rooms.append(room)
      else:
        attempts -= 1
    return rooms

  def gen_room(floor, kind=Room):
    room_width = choice(ROOM_WIDTHS)
    room_height = choice(ROOM_HEIGHTS)
    return kind((room_width, room_height))

  def gen_place(floor, feature):
    valid_slots = feature.filter_slots(floor.slots)
    if valid_slots:
      feature.cell = choice(valid_slots)
      floor.mark(feature)
      return True
    else:
      return False

  def gen_neighbor(floor, node, neighbor):
    valid_slots = neighbor.filter_slots(floor.slots)
    overlap = []
    while valid_slots and not overlap:
      neighbor.cell = choice(valid_slots)
      overlap = set(node.get_exits()) & set(neighbor.get_edges())
      if not overlap:
        valid_slots.remove(neighbor.cell)
        neighbor.cell = None
    if overlap:
      door = choice(tuple(overlap))
      floor.mark(neighbor)
      floor.tree.connect(node, neighbor, door)
      return True
    else:
      return False

  def gen_mazes(floor):
    mazes = []
    slots = floor.slots.copy()
    while slots:
      slot = choice(slots)
      slots.remove(slot)
      cells = [slot]
      stack = [slot]
      while slot:
        x, y = slot
        neighbors = [(sx, sy) for sx, sy in slots if (
          abs(sx - x) == 2 and y == sy
          or abs(sy - y) == 3 and x == sx
        )]
        if neighbors:
          neighbor = choice(neighbors)
          neighbor_x, neighbor_y = neighbor
          while x != neighbor_x:
            x += 1 if x < neighbor_x else -1
            cells.append((x, y))
          while y != neighbor_y:
            y += 1 if y < neighbor_y else -1
            cells.append((x, y))
          stack.append(neighbor)
          slots.remove(neighbor)
          slot = neighbor
        elif len(stack) > 1:
          stack.pop()
          slot = stack[-1]
        else:
          slot = None
      mazes.append(Maze(cells))
      for maze in mazes:
        floor.mark(maze)

  def gen_loop(floor):
    tree = floor.tree
    graph = floor.graph
    stage = floor.stage
    ends = [n for n in tree.ends() if type(n) is Room or not isinstance(n, Room)]
    if not ends:
      return False
    node = choice(ends)
    neighbors = [n for n in graph.neighbors(node) if (
      (type(n) is Room or not isinstance(n, Room))
      and n not in tree.neighbors(node)
      and (
        type(n) is Maze and tree.degree(n) == 1
        or tree.distance(node, n) > 2
      )
    )]
    if neighbors:
      neighbor = choice(neighbors)
      connectors = graph.connectors(node, neighbor)
      connector = choice(connectors)
      tree.connect(node, neighbor, connector)
      return True
    else:
      return False

  def gen_loops(floor):
    success = True
    while success:
      success = floor.gen_loop()

  def gen_minirooms(floor):
    graph = floor.graph
    stage = floor.stage

    mazes = []
    rooms = []
    for node in graph.nodes:
      if type(node) is Maze:
        mazes.append(node)
      else:
        rooms.append(node)

    room_borders = []
    for room in rooms:
      room_borders += room.get_border()

    maze_cells = []
    for maze in mazes:
      maze_cells += maze.get_cells()

    mini_rooms = []
    def place_room(cell, vertical=False, align_right=False, align_bottom=False):
      major_axis = randint(2, 6)
      if vertical:
        room_size = (2, major_axis)
      else:
        room_size = (major_axis, 2)

      room_width, room_height = room_size
      cell_x, cell_y = cell
      if align_right:
        cell_x -= room_width - 1
      if align_bottom:
        cell_y -= room_height - 1

      mini_room = Room(room_size)
      mini_room.cell = (cell_x, cell_y)
      for cell in mini_room.get_cells() + mini_room.get_border():
        if (cell in room_borders
        or cell not in maze_cells and stage.get_tile_at(cell) is not stage.WALL):
          break
      else:
        mini_rooms.append(mini_room)
        return True
      return False

    choices = maze_cells.copy()
    while choices:
      cell = choice(choices)
      choices.remove(cell)
      if place_room(cell, 0, 0, 0): continue
      if place_room(cell, 0, 0, 1): continue
      if place_room(cell, 0, 1, 0): continue
      if place_room(cell, 0, 1, 1): continue
      if place_room(cell, 1, 0, 0): continue
      if place_room(cell, 1, 0, 1): continue
      if place_room(cell, 1, 1, 0): continue
      if place_room(cell, 1, 1, 1): continue

    for room in mini_rooms:
      corners = room.get_corners()
      for cell in room.get_cells():
        if cell not in corners or randint(1, 2) == 1:
          stage.set_tile_at(cell, stage.FLOOR)

  def draw_door(floor, cell, door, room=None):
    stage = floor.stage
    x, y = cell
    door_cell = cell
    doorway_cell = None
    if (stage.get_tile_at((x - 1, y)) is stage.WALL
    and stage.get_tile_at((x + 1, y)) is stage.WALL):
      if stage.get_tile_at((x, y - 1)) is stage.WALL:
        door_cell = (x, y - 1)
        doorway_cell = cell
      elif stage.get_tile_at((x, y + 1)) is stage.WALL:
        doorway_cell = (x, y + 1)
    if doorway_cell:
      stage.set_tile_at(doorway_cell, stage.DOOR_WAY)
    stage.set_tile_at(door_cell, stage.DOOR_WAY)
    stage.spawn_elem_at(door_cell, door)

  def connect(floor):
    graph = floor.graph
    nodes = graph.nodes
    for node in nodes:
      others = [n for n in nodes if n is not node]
      edges = []
      for edge in node.get_edges():
        neighbor = next((n for n in others if edge in n.get_edges()), None)
        if neighbor:
          graph.connect(node, neighbor, edge)
          edges.append(edge)
      if not edges:
        return False
    return True

  def span(floor, start=None):
    graph = floor.graph
    tree = floor.tree
    if start is None:
      start = choice([n for n in graph.nodes if (
        type(n) is not Maze
        and (tree.degree(n) < n.degree
          or n.degree == 0)
      )])
    queue = [start]
    while queue:
      node = queue[-1]
      tree.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n in neighbors if (
        not tree.connectors(node, n)
        and (tree.degree(n) == 0
          or n.degree and tree.degree(n) != n.degree)
      )]
      if not neighbors or node.degree and tree.degree(node) == node.degree:
        if tree.degree(node) < node.degree:
          debug("{node} has too few connections (expected {expected_degree}, got {observed_degree})".format(
            node=type(node).__name__,
            expected_degree=node.degree,
            observed_degree=tree.degree(node),
          ))
          return False
        debug("Span from {node} complete".format(node=type(node).__name__))
        queue.pop()
        continue
      debug("Spanning from {node}".format(node=type(node).__name__))
      for neighbor in neighbors:
        connectors = graph.connectors(node, neighbor)
        connector = choice(connectors)
        debug("Connecting {node}({node_observed_degree}/{node_expected_degree}°) to {neighbor}({neighbor_observed_degree}/{neighbor_expected_degree}°)".format(
          node=type(node).__name__,
          node_observed_degree=tree.degree(node),
          node_expected_degree=node.degree,
          neighbor=type(neighbor).__name__,
          neighbor_observed_degree=tree.degree(neighbor),
          neighbor_expected_degree=neighbor.degree,
        ))
        tree.connect(node, neighbor, connector)
        if tree.degree(neighbor) < neighbor.degree or neighbor.degree == 0:
          debug("Queueing neighbor {node}({observed_degree}/{expected_degree}°)".format(
            node=type(neighbor).__name__,
            observed_degree=tree.degree(node),
            expected_degree=node.degree
          ))
          queue.insert(0, neighbor)
        else:
          debug("Neighbor {node} has enough connections, skipping...".format(node=type(neighbor).__name__))
        if node.degree:
          if tree.degree(node) == node.degree:
            break
          if tree.degree(node) > node.degree:
            debug("{node} has too many connections (expected {expected_degree}, got {observed_degree})".format(
              node=type(node).__name__,
              expected_degree=node.degree,
              observed_degree=tree.degree(node),
            ))
            return False
      if type(node) is Maze:
        queue.remove(node)
        queue.insert(0, node)
    for node in graph.nodes:
      if node.degree and tree.degree(node) < node.degree:
        return False
    return True

  def fill_ends(floor):
    tree = floor.tree
    stage = floor.stage
    mazes = [n for n in tree.nodes if type(n) is Maze]
    doors = [c[0] for _, c in tree.conns.items()]
    for maze in mazes:
      stack = maze.get_ends()
      while stack:
        end = stack.pop()
        door = next((d for d in doors if is_adjacent(d, end)), None)
        if door is None or tree.degree(maze) == 1:
          adjs = [c for c in maze.cells if is_adjacent(c, end)]
          if len(adjs) <= 1 and end in maze.cells:
            maze.cells.remove(end)
            stage.set_tile_at(end, stage.WALL)
          if len(adjs) == 1:
            stack.append(adjs[0])
      if tree.degree(maze) <= 1:
        tree.remove(maze)

  def fill_isolated(floor):
    tree = floor.tree
    graph = floor.graph
    stage = floor.stage
    isolated = [n for n in graph.nodes if (
      n not in tree.nodes
      and (type(n) is Room or type(n) is Maze)
    )]
    for node in isolated:
      for cell in node.get_cells():
        stage.set_tile_at(cell, stage.WALL)
      graph.disconnect(node)
    graph.nodes = tree.nodes

def debug(*message):
  if config.DEBUG:
    print("[DEBUG]", *message)

def gen_debug(seed=None):
  floor = Floor((13, 13))
  room = Room((11, 11))
  room.cell = (1, 1)
  stage = floor.stage
  stage.seed = seed
  stage.fill(stage.WALL)
  floor.mark(room)
  stage.entrance = room.get_center()

  stage.spawn_elem_at((stage.entrance[0] - 2, stage.entrance[1]), Coffin())
  stage.set_tile_at((stage.entrance[0] + 2, stage.entrance[1]), stage.PIT)
  return stage

def gen_features(floor, feature_graph):
  for node in feature_graph.nodes:
    if node not in floor.tree.nodes:
      if not floor.gen_place(node):
        return False
      floor.tree.add(node)
      debug("Placed {}".format(type(node).__name__))
    neighbors = feature_graph.neighbors(node)
    for neighbor in neighbors:
      if neighbor not in floor.tree.nodes:
        debug("Attempting to place {neighbor} from {node}".format(
          node=type(node).__name__,
          neighbor=type(neighbor).__name__
        ))
        if not floor.gen_neighbor(node, neighbor):
          return False
        debug("Placed {neighbor} from {node}".format(
          node=type(node).__name__,
          neighbor=type(neighbor).__name__
        ))
        floor.tree.add(neighbor)
  return True

def gen_floor(features, entrance=None, size=config.FLOOR_SIZE, seed=None):
  lkg = None
  iters = 0
  while lkg is None:
    iters += 1
    debug("-- Iteration {} --".format(iters))
    floor = Floor(size)
    if seed is None:
      seed = getrandbits(32)
    random.seed(seed)
    tree = floor.tree
    graph = floor.graph
    stage = floor.stage
    stage.seed = seed
    seed = None

    if not gen_features(floor, features):
      debug("Feature placement failed")
      yield None
      continue

    empty_rooms = floor.gen_rooms()
    if not empty_rooms:
      debug("No usable rooms generated")
      yield None
      continue

    floor.gen_mazes()

    if not floor.connect():
      debug("Failed to connect feature graph")
      yield None
      continue

    if not floor.span():
      debug("Failed to satisfy feature degree constraints")
      yield None
      continue

    # floor.gen_loops()
    floor.fill_ends()
    floor.fill_isolated()

    isolated = [f for f in features.nodes if f not in tree.nodes]
    if isolated:
      debug("Failed to connect all features")
      yield None
      continue

    secrets = [n for n in tree.nodes if n.secret]
    for node in secrets:
      neighbors = tree.neighbors(node)
      if len(neighbors) == 1 and type(neighbors[0]) is Maze:
        maze = neighbors[0]
        door = tree.connectors(node, maze)[0]
        if [e for e in maze.get_ends() if is_adjacent(e, door)]:
          debug("Hidden room connected to dead end")
          yield None
          continue

    for feature in graph.nodes:
      feature.place(floor.stage, tree.connectors(feature))

    floor.gen_minirooms()

    empty_rooms = [r for r in empty_rooms if r in tree.nodes]
    door_cells = [d for cs in tree.conns.values() for d in cs]

    # draw corners
    for room in empty_rooms:
      corners = [c for c in room.get_corners() if not [
        d for d in door_cells if manhattan(c, d) <= 2]]
      if corners:
        corner_count = randrange(0, len(corners))
        for i in range(corner_count):
          corner = choice(corners)
          stage.set_tile_at(corner, stage.WALL)

    # set entrance
    if entrance:
      entry_room = entrance
    else:
      if not empty_rooms:
        debug("No empty rooms to spawn at")
        yield None
        continue
      empty_leaves = [n for n in empty_rooms if tree.degree(n) == 1]
      if not empty_leaves:
        debug("No empty leaves to spawn at")
        yield None
        continue
      entry_room = choice(empty_leaves)
    center_x, center_y = entry_room.get_center()
    stage.entrance = (center_x, center_y + 0)
    if entry_room in empty_rooms or type(entry_room) is VerticalRoom:
      if entry_room in empty_rooms:
        empty_rooms.remove(entry_room)
      stage.set_tile_at(stage.entrance, stage.STAIRS_DOWN)

    # draw doors
    doors = []
    for (n1, n2), conns in tree.conns.items():
      if n1.secret or tree.degree(n1) == 1 and not n1 is entry_room:
        origin = n2
        target = n1
      elif n2.secret or tree.degree(n2) == 1 and not n2 is entry_room:
        origin = n1
        target = n2
      elif isinstance(n2, Room):
        origin = n1
        target = n2
      elif isinstance(n1, Room):
        origin = n2
        target = n1
      if isinstance(target, Room) and target.EntryDoor is not Door:
        door = target.EntryDoor()
      elif isinstance(origin, Room) and origin.ExitDoor is not Door:
        door = origin.ExitDoor()
      else:
        door = Door()
      debug(type(origin).__name__, type(target).__name__, type(door).__name__)
      doors.append(door)
      for door_cell in conns:
        if door_cell in doors:
          continue
        floor.draw_door(door_cell, door, room=target)

    # spawn enemies
    for room in empty_rooms:
      enemy_count = randint(0, 3)
      valid_cells = [c for c in room.get_cells() if not [d for d in door_cells if manhattan(d, c) <= 2]]
      while enemy_count and valid_cells:
        cell = choice(valid_cells)
        valid_cells.remove(cell)
        if stage.get_tile_at(cell) is stage.FLOOR:
          stage.spawn_elem_at(cell, gen_enemy(choices((Eye, Mushroom), (5, 1))[0]))
          enemy_count -= 1
          if room in empty_rooms:
            empty_rooms.remove(room)

    # spawn key if necessary
    if next((d for d in doors if type(d) is TreasureDoor), None):
      common_leaves = [r for r in tree.nodes if tree.degree(r) == 1 and type(r) is Room]
      if not common_leaves:
        debug("No empty rooms to spawn key at")
        yield None
        continue
      key_room = choice(common_leaves)
      if key_room in empty_rooms:
        empty_rooms.remove(key_room)
      stage.spawn_elem_at(key_room.get_center(), Chest(Key))

    # spawn items
    for room in empty_rooms:
      ItemRoom(
        size=room.size,
        cell=room.cell,
        items=[gen_item() for _ in range(randint(1, 3))]
      ).place(stage, connectors=door_cells)

    debug("-- Generation succeeded in {iters} iteration{s} --".format(
      iters=iters,
      s="" if iters == 1 else "s"
    ))
    lkg = stage

  yield lkg

def gen_enemy(Enemy, *args, **kwargs):
  return Enemy(
    ailment=("sleep" if randint(1, 3) == 1 else None),
    *args, **kwargs
  )

def gen_item():
  return choices(
    (Potion, Cheese, Bread, Fish, Antidote),
    (     2,      4,     3,    1,        3)
  )[0]
