import random
from random import randint, randrange, choice, choices
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
from dungeon.features.battleroom import BattleRoom
from dungeon.features.treasureroom import TreasureRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.coffinroom import CoffinRoom
from dungeon.features.pitroom import PitRoom
from dungeon.features.elevroom import ElevRoom

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
from dungeon.props.block import Block
from dungeon.props.door import Door
from dungeon.props.battledoor import BattleDoor
from dungeon.props.treasuredoor import TreasureDoor
from dungeon.props.coffin import Coffin
from dungeon.props.soul import Soul

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

def cells(size):
  cells = []
  width, height = size
  for y in range(height):
    for x in range(width):
      cells.append((x, y))
  return cells

def get_neighbors(nodes, node):
  neighbors = {}
  others = [n for n in nodes if n is not node]
  for edge in node.get_edges():
    neighbor = next((n for n in others if edge in n.get_edges()), None)
    if neighbor:
      if neighbor not in neighbors:
        neighbors[neighbor] = [edge]
      else:
        neighbors[neighbor].append(edge)
  return neighbors

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
      overlap = set(node.get_edges()) & set(neighbor.get_exits())
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

  def draw_door(floor, cell, tile=Stage.DOOR, room=None):
    x, y = cell
    stage = floor.stage
    door_cell = cell
    doorway_cell = None
    doorway_offset = 1
    if (stage.get_tile_at((x - 1, y)) is stage.WALL
    and stage.get_tile_at((x + 1, y)) is stage.WALL):
      if (stage.get_tile_at((x - 1, y - 1)) is stage.WALL
      and stage.get_tile_at((x + 1, y - 1)) is stage.WALL
      and stage.get_tile_at((x, y + 1)) is stage.FLOOR):
        doorway_offset = -1
      elif (stage.get_tile_at((x - 1, y + 1)) is stage.WALL
      and stage.get_tile_at((x + 1, y + 1)) is stage.WALL):
        doorway_offset = 1
      doorway_cell = (x, y + doorway_offset)
      if room and doorway_offset != -1:
        _, target_y = room.get_center()
        if doorway_offset * (target_y - y) > 0:
          doorway_cell = cell
          door_cell = (x, y + doorway_offset)
    if doorway_cell:
      stage.set_tile_at(doorway_cell, stage.DOOR_WAY)
    stage.set_tile_at(door_cell, stage.FLOOR) # tile)
    if type(room) is BattleRoom:
      door = BattleDoor()
    elif type(room) is TreasureRoom:
      door = TreasureDoor()
    else:
      door = Door()
    stage.spawn_elem(door, door_cell)

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
      start = choice(graph.nodes)
    queue = [start]
    while queue:
      node = queue[-1]
      tree.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n in neighbors if (
        tree.degree(n) == 0
        # not tree.connectors(node, n)
        # and tree.degree(n) < n.degree or n.degree == 0
      )]
      if not neighbors:
        if tree.degree(node) < node.degree:
          return False
        queue.pop()
        continue
      for neighbor in neighbors:
        connectors = graph.connectors(node, neighbor)
        connector = choice(connectors)
        tree.connect(node, neighbor, connector)
        queue.insert(0, neighbor)
        if node.degree:
          if tree.degree(node) == node.degree:
            break
          if tree.degree(node) > node.degree:
            return False
      if type(node) is Maze:
        queue.remove(node)
        queue.insert(0, node)
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

  stage.spawn_elem(Coffin(), (stage.entrance[0] - 2, stage.entrance[1]))
  stage.set_tile_at((stage.entrance[0] + 2, stage.entrance[1]), stage.PIT)
  return stage

def gen_features(floor, features):
  for group in features:
    root = group[0]
    if not floor.gen_place(root):
      return False
    if len(group) > 1:
      floor.tree.add(root)
    for feature in group[1:]:
      if not floor.gen_neighbor(root, feature):
        return False
      floor.tree.add(feature)
  return True

def gen_floor(seed=None):
  floor = Floor(config.FLOOR_SIZE)
  if seed is None:
    seed = random.getrandbits(32)
  random.seed(seed)
  tree = floor.tree
  graph = floor.graph
  stage = floor.stage
  stage.seed = seed

  arena = BattleRoom()
  exit_room = ExitRoom()
  puzzle_room = VerticalRoom((5, 4))
  treasure_room = TreasureRoom()
  oasis_room = OasisRoom()
  coffin_room = CoffinRoom()
  pit_room = PitRoom()
  elev_room = ElevRoom()

  features = [
    [arena, exit_room, puzzle_room],
    # [pit_room],
    # [elev_room],
    [treasure_room],
    [oasis_room],
    # [coffin_room],
  ]

  if not gen_features(floor, features):
    debug("Feature placement failed")
    return gen_floor()

  empty_rooms = floor.gen_rooms()
  # if not empty_rooms:
  #   debug("No usable rooms generated")
  #   return gen_floor()

  floor.gen_mazes()

  if not floor.connect():
    debug("Failed to connect feature graph")
    return gen_floor()

  if not floor.span(start=puzzle_room):
    debug("Failed to satisfy feature degree constraints")
    return gen_floor()

  floor.gen_loops()
  floor.fill_ends()
  floor.fill_isolated()

  feature_list = [f for g in features for f in g]
  isolated = [f for f in feature_list if f not in tree.nodes]
  if isolated:
    debug("Failed to connect all features")
    return gen_floor()

  secrets = [n for n in tree.nodes if n.secret]
  for node in secrets:
    neighbors = tree.neighbors(node)
    if len(neighbors) == 1 and type(neighbors[0]) is Maze:
      maze = neighbors[0]
      door = tree.connectors(node, maze)[0]
      if [e for e in maze.get_ends() if is_adjacent(e, door)]:
        debug("Hidden room connected to dead end")
        return gen_floor()

  for feature in graph.nodes:
    feature.place(floor.stage)

  floor.gen_minirooms()

  # draw doors
  doors = []
  for (n1, n2), conns in tree.conns.items():
    if n1.secret or tree.degree(n1) == 1:
      room = n1
    elif n2.secret or tree.degree(n2) == 1:
      room = n2
    elif isinstance(n1, Room):
      room = n1
    elif isinstance(n2, Room):
      room = n2
    else:
      room = None
    for door in conns:
      if door in doors:
        continue
      tile = stage.DOOR_HIDDEN if n1.secret or n2.secret else stage.DOOR
      floor.draw_door(door, tile, room)
      doors.append(door)

  empty_rooms = [r for r in empty_rooms if r in tree.nodes]
  if not empty_rooms:
    debug("No empty rooms to spawn at")
    return gen_floor()

  # draw corners
  for room in empty_rooms:
    corners = [c for c in room.get_corners() if not [
      d for d in doors if manhattan(c, d) <= 2]]
    if corners:
      corner_count = randrange(0, len(corners))
      for i in range(corner_count):
        corner = choice(corners)
        stage.set_tile_at(corner, stage.WALL)

  stage.rooms = empty_rooms + feature_list
  empty_leaves = [n for n in empty_rooms if tree.degree(n) == 1]
  if not empty_leaves:
    debug("No empty leaves to spawn at")
    return gen_floor()

  entry_room = choice(empty_leaves)
  center_x, center_y = entry_room.get_center()
  stage.entrance = (center_x, center_y + 0)
  if entry_room in empty_rooms:
    empty_rooms.remove(entry_room)
    stage.set_tile_at(stage.entrance, stage.STAIRS_DOWN)

  for room in empty_rooms:
    valid_cells = [c for c in room.get_cells() if not [d for d in doors if manhattan(d, c) <= 2]]
    enemy_count = randint(0, 3)
    i = 0
    while i < enemy_count and valid_cells:
      cell = choice(valid_cells)
      valid_cells.remove(cell)
      stage.spawn_elem(gen_enemy(1), cell)
      i += 1

  if not empty_rooms:
    debug("No empty rooms to spawn key at")
    return gen_floor()
  key_room = choice(empty_rooms)
  empty_rooms.remove(key_room)
  stage.spawn_elem(Chest(Key), key_room.get_center())

  genie = Genie(name="Joshin", script=(
    ("Joshin", "Pee pee poo poo"),
    ("Minxia", "He has such a way with words")
  ))
  corner = next((c for c in entry_room.get_corners() if (
    stage.get_tile_at(c) is stage.FLOOR
    and not [d for d in doors if manhattan(d, c) <= 2]
  )), None)
  if corner:
    stage.spawn_elem(genie, corner)

  stage.spawn_elem(Block(), (center_x, center_y - 1))
  return stage

def gen_enemy(floor):
  if floor == 1:
    return choices((Eye, Mushroom), (5, 1))[0]()
  elif floor == 2:
    return choices((Eye, Mushroom), (3, 1))[0]()
  else:
    return choices((Eye, Mushroom, Skeleton), (2, 2, 1))[0]()

def gen_item():
  return choices(
    (Potion, Ankh, Cheese, Bread, Fish, Antidote, Emerald),
    (     3,    1,      4,     3,    1,        3,       1)
  )[0]()
