import random
from lib.cell import is_odd, add, is_adjacent, manhattan

from dungeon.stage import Stage
from dungeon.room import Room
from dungeon.maze import Maze

from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.mushroom import Mushroom
from actors.skeleton import Skeleton
from actors.mimic import Mimic
from actors.npc import NPC

from props.chest import Chest
from props.soul import Soul

from items.hp.potion import Potion
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.sp.cheese import Cheese
from items.sp.bread import Bread
from items.sp.fish import Fish
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.ailment.antidote import Antidote

from skills.shieldbash import ShieldBash
from skills.fulgur import Fulgur
from skills.sana import Sana
from skills.virus import Virus
from skills.hpup import HpUp
from skills.caladbolg import Caladbolg
from skills.longinus import Longinus
from skills.mjolnir import Mjolnir

from dungeon.features.battleroom1 import BattleRoom as BattleRoom1
from dungeon.features.battleroom2 import BattleRoom as BattleRoom2
from dungeon.features.treasureroom import TreasureRoom

possible_widths = (3, 5, 7)
possible_heights = (4, 7)

def cells(size):
  cells = []
  (width, height) = size
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

class Dungeon:
  def __init__(dungeon):
    dungeon.nodes = []
    dungeon.conns = {}

  def get_node_neighbors(dungeon, node):
    neighbors = {}
    for edge in node.get_edges():
      x, y = edge
      edge_neighbors = [n for n in dungeon.get_conn_neighbors(dungeon, edge) if n is not node]
      for neighbor in edge_neighbors:
        if neighbor in neighbors:
          neighbors[neighbor].append(edge)
        else:
          neighbors[neighbor] = [edge]
    return neighbors

  def get_conn_neighbors(dungeon, conn):
    neighbors = []
    x, y = conn
    adj_cells = (
      (x - 1, y),
      (x, y - 1),
      (x + 1, y),
      (x, y + 1)
    )
    for cell in adj_cells:
      for neighbor in dungeon.nodes:
        if cell in neighbor.get_cells():
          neighbors.append(neighbor)
    return neighbors

  def connect(dungeon, node_a, node_b, conn):
    dungeon.conns[node_a, node_b] = conn
    dungeon.conns[node_b, node_a] = conn

def split_at(dungeon, conn):
  (node_a, node_b) = dungeon.get_conn_neighbors(conn)

  def flood_fill(node, graph):
    nodes, conns = graph
    nodes.append(node)
    neighbors = dungeon.get_node_neighbors(node)
    neighbors = [n for n, c in neighbors if c is not conn and n not in nodes]
    for neighbor, conn in neighbors:
      flood_fill(node)
      conns[node, neighbor] = conn
      conns[neighbor, node] = conn

  graph_a = flood_fill(node_a, ([], {}))
  if len(graph_a.nodes) == len(dungeon.nodes):
    return None
  graph_b = flood_fill(node_b, ([], {}))
  return (graph_a, graph_b)

def debug_gen():
  stage = Stage((9, 9))
  stage.fill(Stage.WALL)
  stage.entrance = (1, 1)
  slots = [(x, y) for x, y in stage.get_cells() if (
    x % 2 == 1
    and y % 3 == 1
  )]
  mazes = gen_mazes(slots)
  for maze in mazes:
    for x, y in maze.get_cells():
      stage.set_tile_at((x, y), Stage.FLOOR)
  return dungeon((27, 27), 2)

def debug_floor():
  floor = parse_data([
    "  #####  ",
    " ##...## ",
    " #.....# ",
    " #.....# ",
    " #.....# ",
    " ##...## ",
    "  ##+##  ",
    "    .    ",
    "    .    ",
    "    .    ",
    "    .    ",
    " ....... ",
    " ....... ",
    " ....... ",
    " ....... ",
    " ....... ",
    "         "
  ])
  floor.rooms = [
    Room((5, 5), (2, 1)),
    Room((7, 5), (1, 11)),
  ]
  floor.entrance = (4, 3)
  floor.set_tile_at(floor.entrance, Stage.STAIRS_DOWN)
  floor.spawn_elem(Skeleton(), (2, 14))
  floor.spawn_elem(Soul(Fulgur), (3, 14))
  floor.spawn_elem(Soul(Sana), (4, 14))
  floor.spawn_elem(Soul(Virus), (5, 14))
  floor.spawn_elem(Soul(HpUp), (6, 14))
  return floor

def top_floor():
  floor = parse_data([
    "#####-#####################",
    "   .....                   ",
    "   .....                   ",
    "   .....                   ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "     .                     ",
    "#####.#####################",
    "#####+#####################",
    "##.......##################",
    "##.......*....#############",
    "##.......####.#...........#",
    "##.......####.#...........#",
    "##.......####.#..       ..#",
    "#####.#######.#..  ...  ..#",
    "#####.#######.+.!  .......#",
    "#####.#########..  ...  ..#",
    "####...########..       ..#",
    "###..>..#######...........#",
    "####...########...........#",
    "#####.#####################",
    "###########################"
  ])

  floor.rooms = [
    Room((5, 3), (3, 1)),
    Room((7, 5), (2, 16)),
    Room((11, 9), (15, 18))
  ]

  floor.spawn_elem(Mimic(), (20, 22))
  floor.spawn_elem(NPC(), (4, 1))

  return floor

def parse_data(data):
  rows = len(data)
  cols = len(data[0])
  floor = Stage((cols, rows))
  entrance = None
  stairs = None
  x, y = (0, 0)
  for row in data:
    x = 0
    for char in row:
      cell = (x, y)
      tile = Stage.FLOOR
      if char == "#":
        tile = Stage.WALL
      elif char == " ":
        tile = Stage.PIT
      elif char == "+":
        tile = Stage.DOOR
      elif char == "-":
        tile = Stage.DOOR_LOCKED
      elif char == "*":
        tile = Stage.DOOR_HIDDEN
      elif char == "!":
        tile = Stage.MONSTER_DEN
      elif char == ">":
        tile = Stage.STAIRS_DOWN
        entrance = cell
      elif char == "<":
        tile = Stage.STAIRS_UP
        stairs = cell
      floor.set_tile_at(cell, tile)
      x += 1
    y += 1
  floor.entrance = entrance
  floor.stairs = stairs
  return floor

def giant_room(size):
  stage = Stage(size)
  width, height = size
  stage.fill(Stage.WALL)
  room = Room((width - 2, height - 2), (1, 1))
  for cell in room.get_cells():
    stage.set_tile_at(cell, Stage.FLOOR)
  stage.rooms.append(room)

  cells = []
  for y in range(width - 4):
    for x in range(height - 4):
      cells.append((x + 2, y + 2))

  entrance = random.choice(cells)
  stage.set_tile_at(entrance, Stage.STAIRS_DOWN)
  cells.remove(entrance)
  cells = [c for c in cells if manhattan(c, entrance) >= 3]

  stairs = random.choice(cells)
  stage.set_tile_at(stairs, Stage.STAIRS_UP)
  cells.remove(stairs)
  cells = [c for c in cells if manhattan(c, stairs) >= 3]

  for cell in cells:
    if random.randint(1, 25) != 1:
      continue
    if random.randint(1, 3) == 1:
      item = random.choices((Cheese, Bread, Fish, Potion, Ankh, Emerald), (3, 2, 1, 2, 1, 1))[0]()
      stage.spawn_elem(Chest(item), cell)
    else:
      enemy = random.choices((Eye, Mushroom, Mimic), (4, 2, 1))[0]()
      stage.spawn_elem(enemy, cell)
      if type(enemy) is not Mimic and random.randint(0, 2):
        enemy.ailment = "sleep"

  stage.entrance = entrance
  stage.stairs = stairs
  return stage

def dungeon(size, floor=1):
  width, height = size
  stage = Stage((width, height))
  stage.fill(Stage.WALL)
  slots = [(x, y) for x, y in stage.get_cells() if (
    x % 2 == 1
    and y % 3 == 1
  )]

  entry_room = None
  exit_room = None
  doors = []
  features = []

  floor = 2
  if floor == 1:
    feature = BattleRoom1()
  if floor == 2:
    feature = TreasureRoom()
  elif floor == 4:
    feature = BattleRoom2()
  else:
    feature = None

  if feature:
    valid_slots = []
    padded_slots = [(x, y) for x, y in slots if (
      x > 1 and x < width - 2
      and y > 1 and y < height - 2
    )]
    for slot in padded_slots:
      offset_cells = [add(cell, slot) for cell in feature.get_cells()]
      offset_cells = [(x, y) for x, y in offset_cells if (
        x % 2 == 1
        and y % 3 == 1
      )]
      for cell in offset_cells:
        if cell not in padded_slots:
          break
      else:
        valid_slots.append(slot)
    slot = random.choice(valid_slots)
    feature.place(stage, slot)
    for cell in feature.get_cells():
      if cell in slots:
        slots.remove(cell)
    features.append(feature)
    for room in stage.rooms:
      for cell in room.get_cells():
        if stage.get_tile_at(cell) is Stage.STAIRS_UP:
          exit_room = room
          break

  slots_before = slots.copy()
  rooms = gen_rooms(slots)
  if len(rooms) == 1:
    print("restart: Too few rooms")
    return dungeon(size, floor)

  if entry_room:
    rooms.insert(0, entry_room)
    rooms.insert(1, exit_room)

  mazes = gen_mazes(slots)

  node_conns = {}
  conn_nodes = {}
  nodes = rooms + mazes + features
  for node in nodes:
    node_conns[node] = []

  if exit_room and exit_room in nodes:
    nodes.remove(exit_room)

  node = random.choice(nodes)
  nodes.remove(node)
  stack = [node]
  while node:
    neighbors = get_neighbors(nodes, node)
    # only connect to neighbors that this neighbor hasn't connected to before
    targets = [neighbor for neighbor in list(neighbors.keys()) if (
      next((target for target, conn in node_conns[node] if target is neighbor), None) is None
    )]
    if targets:
      # pick a random neighbor
      neighbor = random.choice(targets)

      # pick a random connector
      conn = random.choice(neighbors[neighbor])

      # mark connector as door
      doors.append(conn)

      # connect this node to that neighbor
      node_conns[node].append((neighbor, conn))
      node_conns[neighbor].append((node, conn))
      conn_nodes[conn] = (node, neighbor)

      # only add neighbor to the stack if it's not visited
      if neighbor in nodes:
        stack.append(neighbor)

      # declare neighbor as visited (chance of creating loops)
      if random.randint(1, 10) != 1 or neighbor in features:
        nodes.remove(neighbor)

      # use neighbor for next iteration
      if neighbor not in features:
        node = neighbor
    else:
      stack.remove(node)
      node = stack[-1] if stack else None

  for node in nodes:
    if node in features:
      print("restart: Unconnected feature")
      return dungeon(size, floor)

  for maze in mazes:
    # remove dead ends
    if len(node_conns[maze]) == 1:
      neighbor, conn = node_conns[maze][0]
      doors.remove(conn)

    stack = maze.get_ends()
    while stack:
      end = stack.pop()
      door = next((d for d in doors if is_adjacent(d, end)), None)
      if door is None:
        neighbors = [c for c in maze.cells if is_adjacent(c, end)]
        if len(neighbors) <= 1 and end in maze.cells:
          maze.cells.remove(end)
        if len(neighbors) == 1:
          stack.append(neighbors[0])
    if len(maze.cells) <= 1:
      mazes.remove(maze)

  for maze in mazes:
    if len(maze.cells) / (len(node_conns[maze]) or 1) >= 12:
      print("restart: Corridor too long")
      return dungeon(size, floor)

  for node in rooms + mazes:
    for cell in node.get_cells():
      stage.set_tile_at(cell, Stage.FLOOR)

  # from a door, we need to get the list of rooms it connects to
  # if we think of a dungeon as a maze, the dead ends are where we wanna put special stuff
  # a dungeon is a bit more than a maze though: it has connections between nodes
  # conn = node_conns[node]
  # node = conn_nodes[conn]
  # we need to be able to traverse the graph
  # neighbors(node) -> (other_node, conn)

  secret_rooms = []
  dead_ends = []
  for door in doors:
    x, y = door
    for room in rooms:
      if room is entry_room or room is exit_room or len(node_conns[room]) != 1:
        continue
      _, conn_door = node_conns[room][0]
      if conn_door == door:
        if floor != 1 and random.randint(1, 5) == 1:
          secret_rooms.append(room)
          stage.set_tile_at(door, Stage.DOOR_HIDDEN)
        else:
          dead_ends.append(room)
          stage.set_tile_at(door, Stage.DOOR)
        if stage.get_tile_at((x - 1, y)) is Stage.WALL and stage.get_tile_at((x + 1, y)) is Stage.WALL:
          stage.set_tile_at((x, y - 1), Stage.FLOOR)
          stage.set_tile_at((x, y + 1), Stage.FLOOR)
        break
    else:
      stage.set_tile_at(door, Stage.DOOR)
      if stage.get_tile_at((x - 1, y)) is Stage.WALL and stage.get_tile_at((x + 1, y)) is Stage.WALL:
        stage.set_tile_at((x, y - 1), Stage.FLOOR)
        stage.set_tile_at((x, y + 1), Stage.FLOOR)

  if len(rooms) == 1:
    print("restart: Too few rooms")
    return dungeon(size, floor)

  normal_rooms = [r for r in rooms if r not in secret_rooms and r not in dead_ends]
  if len(normal_rooms) < 2:
    print("restart: Too few rooms")
    return dungeon(size, floor)

  if entry_room is None and exit_room is None:
    best = { "steps": 0, "start": None, "end": None }
    for a in normal_rooms:
      local_best = { "steps": 0, "room": None }
      for b in normal_rooms:
        if a is b:
          continue
        steps = manhattan(a.get_center(), b.get_center())
        if steps > local_best["steps"]:
          local_best["steps"] = steps
          local_best["room"] = b
      if local_best["steps"] > best["steps"]:
        best["steps"] = local_best["steps"]
        best["start"] = a
        best["end"] = local_best["room"]
    entry_room = best["start"]
    exit_room = best["end"]
  elif entry_room is None:
    best = None
    for room in normal_rooms + dead_ends:
      dist = manhattan(room.get_center(), exit_room.get_center())
      if best is None:
        best = (dist, room)
      else:
        best_dist, best_room = best
        if dist > best_dist:
          best = (dist, room)
    _, entry_room = best

  stage.entrance = entry_room.get_center()
  stage.set_tile_at(entry_room.get_center(), Stage.STAIRS_DOWN)
  if entry_room in normal_rooms: normal_rooms.remove(entry_room)
  if entry_room in dead_ends: dead_ends.remove(entry_room)

  if exit_room is None:
    exit_room = random.choice(normal_rooms)

  stage.stairs = exit_room.get_center()
  stage.set_tile_at(stage.stairs, Stage.STAIRS_UP)
  if exit_room in normal_rooms:
    normal_rooms.remove(exit_room)

  for room in normal_rooms:
    room_left, room_top = room.cell
    room_width, room_height = room.size
    center_x, center_y = room.get_center()
    if random.randint(1, 10) == 1 and min(room_width, room_height) > 3:
      # giant pit
      radius = 1
      for y in range(room_height - radius * 2):
        for x in range(room_width - radius * 2):
          stage.set_tile_at((room_left + radius + x, room_top + radius + y), Stage.PIT)
    elif random.randint(1, 5) == 1:
      pass
      # # edge-center pits (TODO: random radius)
      # left_tile = stage.get_tile_at((room_left - 1, center_y))
      # right_tile = stage.get_tile_at((room_left + room_width, center_y))
      # top_tile = stage.get_tile_at((center_x, room_top - 1))
      # bottom_tile = stage.get_tile_at((center_x, room_top + room_height))
      # if room_height >= room_width and left_tile is not Stage.DOOR and right_tile is not Stage.DOOR:
      #   y = center_y
      #   for x in range(room_width):
      #     if room_left + x == center_x: continue
      #     stage.set_tile_at((room_left + x, y), Stage.PIT)
      # elif room_width >= room_height and top_tile is not Stage.DOOR and bottom_tile is not Stage.DOOR:
      #   x = center_x
      #   for y in range(room_height):
      #     if room_top + y == center_y: continue
      #     stage.set_tile_at((x, room_top + y), Stage.PIT)
    elif random.randint(1, 30):
      pass
      # fill with pit
      # get all doors
      # if doors >= 2 (always true for normal rooms):
      #   get approximate midpoint of doors that is within room bounds
      #   for each door:
      #     paint from door to midpoint
      # otherwise,
      #   use center as midpoint
      #   paint from door to midpoint
      #
      # paint_x(x1, x2, y)
      # paint_y(y1, y2, x)
      #
      # paint from p1 to p2:
      #   get normal x
      #   get normal y
      #   pick one of two options:
      #     y = y1
      #     while y != y2:
      #       y += normal y
      #     x = x1
      #     while x != x2:
      #       x += normal x
      #   else:
      #     y = y1
      #     while y != y2:
      #       y += normal y
      #     x = x1
      #     while x != x2:
      #       x += normal x

  for room in normal_rooms:
    for cell in room.get_cells():
      is_floor = stage.get_tile_at(cell) is Stage.FLOOR
      is_empty = stage.get_elem_at(cell) is None
      is_beside_door = next((door for door in doors if is_adjacent(door, cell)), None)
      if not is_floor or not is_empty or is_beside_door:
        continue
      if random.randint(1, 25) == 1:
        enemy = gen_enemy(floor)
        stage.spawn_elem(enemy, cell)
        if random.randint(1, 3) == 1:
          enemy.ailment = "sleep"
      elif random.randint(1, 80) == 1:
        item = gen_item()
        stage.spawn_elem(Chest(item), cell)

  for room in dead_ends:
    room_width, room_height = room.size
    max_elems = min(room_width, room_height)
    elems = random.randint(1, max_elems)
    is_door_adjacent = lambda c: next((d for d in doors if manhattan(d, c) <= 2), None)
    cells = [c for c in room.get_cells() if not is_door_adjacent(c)]
    for i in range(elems):
      cell = random.choice(cells)
      cells.remove(cell)
      kind = random.choice(("Item", "Enemy"))
      if kind == "Item":
        item = gen_item()
        stage.spawn_elem(Chest(item), cell)
      elif kind == "Enemy":
        enemy = gen_enemy(floor)
        stage.spawn_elem(enemy, cell)
        if random.randint(1, 3) == 1:
          enemy.ailment = "sleep"

  for room in secret_rooms:
    kind = random.choice(("Treasure", "MonsterDen"))
    for cell in room.get_cells():
      is_floor = stage.get_tile_at(cell) is Stage.FLOOR
      is_empty = stage.get_elem_at(cell) is None
      is_beside_door = next((d for d in doors if manhattan(d, cell) <= 2), None)
      if not is_floor or not is_empty or is_beside_door:
        continue
      if kind == "Treasure" and random.randint(1, 2) == 1:
        if random.randint(1, 10) == 1:
          enemy = Mimic()
          stage.spawn_elem(enemy, cell)
        else:
          item = random.choice((Potion, Elixir, Ankh, Cheese, Bread, Fish, Antidote, Balloon, Emerald))()
          stage.spawn_elem(Chest(item), cell)
      elif kind == "MonsterDen" and random.randint(1, 2) == 1:
        enemy = gen_enemy(10)
        if random.randint(0, 4):
          enemy.ailment = "sleep"
        stage.spawn_elem(enemy, cell)

  stage.rooms.extend(rooms)
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

def gen_rooms(slots):
  rooms = []
  valid_slots = None
  while valid_slots is None or len(valid_slots) > 0:
    room_width = random.choice(possible_widths)
    room_height = random.choice(possible_heights)
    valid_slots = []
    for slot in slots:
      offset_cells = [add(cell, slot) for cell in cells((room_width, room_height))]
      odd_offset_cells = [(x, y) for x, y in offset_cells if (
        x % 2 == 1
        and y % 3 == 1
      )]
      for cell in odd_offset_cells:
        if cell not in slots:
          break
      else:
        valid_slots.append(slot)
    if len(valid_slots) > 0:
      slot = random.choice(valid_slots)
      room = Room((room_width, room_height), slot)
      rooms.append(room)
      for cell in map(lambda cell: add(cell, room.cell), cells(room.size)):
        if cell in slots:
          slots.remove(cell)
  return rooms

def gen_mazes(slots):
  mazes = []
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
  return mazes
