import random
from lib.cell import is_odd, add, is_adjacent, manhattan

import config

from dungeon.stage import Stage
from dungeon.gen.floorgraph import FloorGraph
from dungeon.features.maze import Maze
from dungeon.features.room import Room
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.battleroom import BattleRoom
from dungeon.features.treasureroom import TreasureRoom

from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.actors.eye import Eye
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import NPC

from dungeon.props.chest import Chest
from dungeon.props.soul import Soul

from items.hp.potion import Potion
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.sp.cheese import Cheese
from items.sp.bread import Bread
from items.sp.fish import Fish
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.ailment.antidote import Antidote

possible_widths = (3, 5, 7)
possible_heights = (4, 7)

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

  def place(floor, feature):
    feature.place(floor.stage)
    for cell in feature.get_cells():
      if cell in floor.slots:
        floor.slots.remove(cell)
    floor.graph.add(feature)

  def gen_slots(size):
    slots = []
    width, height = size
    for y in range(height):
      for x in range(width):
        if x % 2 == 1 and y % 3 == 1:
          slots.append((x, y))
    return slots

  def gen_rooms(floor, features=[]):
    rooms = []
    features = features.copy()
    attempts = 3
    while attempts:
      room = features[-1] if features else floor.gen_room()
      if floor.gen_place(room):
        rooms.append(room)
        if features:
          features.pop()
      else:
        attempts -= 1
    return rooms

  def gen_room(floor, kind=Room):
    room_width = random.choice(possible_widths)
    room_height = random.choice(possible_heights)
    return kind((room_width, room_height))

  def gen_place(floor, feature):
    valid_slots = feature.filter_slots(floor.slots)
    if valid_slots:
      feature.cell = random.choice(valid_slots)
      floor.place(feature)
      return True
    else:
      return False

  def gen_neighbor(floor, node, neighbor):
    valid_slots = neighbor.filter_slots(floor.slots)
    overlap = []
    while valid_slots and not overlap:
      neighbor.cell = random.choice(valid_slots)
      overlap = tuple(set(node.get_edges()) & set(neighbor.get_exits()))
      if not overlap:
        valid_slots.remove(neighbor.cell)
        neighbor.cell = None
    if overlap:
      door = random.choice(overlap)
      floor.draw_door(door, target_room=node)
      floor.place(neighbor)
      floor.tree.connect(node, neighbor, door)
      return True
    else:
      return False

  def gen_mazes(floor):
    mazes = []
    slots = floor.slots.copy()
    while slots:
      slot = random.choice(slots)
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
          neighbor = random.choice(neighbors)
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
        floor.place(maze)

  def gen_loops(floor):
    tree = floor.tree
    graph = floor.graph
    stage = floor.stage
    ends = [n for n in tree.ends() if isinstance(n, Room)]
    for end in ends:
      center = end.get_center()
      stage.set_tile_at(end.get_center(), Stage.STAIRS_DOWN)
    end = random.choice(ends)
    stage.set_tile_at(end.get_center(), Stage.STAIRS_UP)
    print(end)
    neighbors = [n for n in graph.neighbors(end) if isinstance(n, Room) and n not in tree.neighbors(end)]
    print(neighbors)

  def draw_door(floor, cell, tile=Stage.DOOR, target_room=None):
    x, y = cell
    stage = floor.stage
    stage.set_tile_at(cell, tile)
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
      stage.set_tile_at((x, y + doorway_offset), stage.DOOR_WAY)
      if target_room:
        _, target_y = target_room.get_center()
        if doorway_offset * (target_y - y) > 0:
          stage.set_tile_at(cell, stage.DOOR_WAY)
          stage.set_tile_at((x, y + doorway_offset), tile)

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
      start = random.choice(graph.nodes)
    queue = [start]
    while queue:
      node = queue[-1]
      tree.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n in neighbors if tree.degree(n) == 0]
      if not neighbors and tree.degree(node) < node.degree:
        return False
      if not neighbors:
        queue.pop()
        continue
      for neighbor in neighbors:
        connectors = graph.connectors(node, neighbor)
        connector = random.choice(connectors)
        tree.connect(node, neighbor, connector)
        queue.append(neighbor)
        if node.degree and tree.degree(node) >= node.degree:
          break
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

def debug_floor(seed=None):
  floor = Floor((27, 27))
  if seed is None:
    seed = random.getrandbits(32)
  random.seed(seed)
  tree = floor.tree
  stage = floor.stage
  stage.seed = seed

  arena = BattleRoom()
  exit_room = Room((3, 4))
  treasure_room = TreasureRoom()
  puzzle_room = VerticalRoom((5, 4), degree=2)
  features = [arena, exit_room, puzzle_room, treasure_room]
  floor.gen_place(arena)
  floor.gen_place(treasure_room)

  if not floor.gen_neighbor(arena, exit_room):
    print("fatal: Failed to place exit room")
    return debug_floor()

  if not floor.gen_neighbor(arena, puzzle_room):
    print("fatal: Failed to place puzzle room")
    return debug_floor()

  tree.add(exit_room) # mark as dead end
  stage.set_tile_at(exit_room.get_center(), Stage.STAIRS_UP)

  floor.gen_rooms()
  floor.gen_mazes()

  if not floor.connect():
    print("fatal: Unconnected feature")
    return debug_floor()

  if not floor.span(start=puzzle_room):
    print("fatal: Failed to satisfy feature degree constraints")
    return debug_floor()

  floor.fill_ends()
  # floor.gen_loops()
  floor.fill_isolated()

  for (n1, n2), doors in tree.conns.items():
    room = n1 if isinstance(n1, Room) else n2 if isinstance(n2, Room) else None
    for door in doors:
      floor.draw_door(door, target_room=room)

  # def distance(r1, r2):
  #   return tree.distance(r1, r2) * 100 + manhattan(r1.get_center(), r2.get_center())
  # entry_room = sorted(rooms, key=lambda r: distance(r, exit_room))[-1]
  rooms = [n for n in tree.nodes if type(n) is Room and n not in features]
  entry_room = random.choice(rooms)
  stage.entrance = entry_room.get_center()
  stage.rooms = rooms + features
  return stage

def gen_enemy(floor):
  if floor == 1:
    return random.choices((Eye, Mushroom), (5, 1))[0]()
  elif floor == 2:
    return random.choices((Eye, Mushroom), (3, 1))[0]()
  else:
    return random.choices((Eye, Mushroom, Skeleton), (2, 2, 1))[0]()

def gen_item():
  return random.choices(
    (Potion, Ankh, Cheese, Bread, Fish, Antidote, Emerald),
    (     3,    1,      4,     3,    1,        3,       1)
  )[0]()
