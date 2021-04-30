import random
from lib.cell import is_odd, add, is_adjacent, manhattan

import config

from dungeon.gen.floorgraph import FloorGraph

from dungeon.stage import Stage
from dungeon.room import Room
from dungeon.features.maze import Maze

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

from dungeon.features.rectroom import RectRoom
from dungeon.features.battleroom import BattleRoom
from dungeon.features.treasureroom import TreasureRoom

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
    attempts = 3
    while attempts:
      if features:
        room = features.pop()
      else:
        room = floor.gen_room()
      if floor.gen_place(room):
        rooms.append(room)
      else:
        attempts -= 1
    return rooms

  def gen_room(floor):
    room_width = random.choice(possible_widths)
    room_height = random.choice(possible_heights)
    return RectRoom((room_width, room_height))

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
    if not valid_slots:
      return False
    edges = []
    while neighbor.cell is None:
      neighbor.cell = random.choice(valid_slots)
      edges = tuple(set(node.get_edges()) & set(neighbor.get_edges()))
      if not edges:
        neighbor.cell = None
    if edges:
      door = random.choice(edges)
      floor.draw_door(door, target=node)
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

  def draw_door(floor, cell, target=None):
    x, y = cell
    stage = floor.stage
    stage.set_tile_at(cell, stage.DOOR)
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
      if target:
        _, target_y = target.get_center()
        if doorway_offset * (target_y - y) > 0:
          stage.set_tile_at(cell, stage.DOOR_WAY)
          stage.set_tile_at((x, y + doorway_offset), stage.DOOR)

  def connect(floor):
    graph = floor.graph
    nodes = graph.nodes
    for node in nodes:
      others = [n for n in nodes if n is not node]
      for edge in node.get_edges():
        neighbor = next((n for n in others if edge in n.get_edges()), None)
        if neighbor:
          graph.connect(node, neighbor, edge)

  def span(floor, start=None):
    graph = floor.graph
    tree = floor.tree
    if start is None:
      start = random.choice(graph.nodes)
    node = start
    stack = [node]
    while node:
      tree.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n in neighbors if tree.degree(n) == 0]
      if neighbors:
        neighbor = random.choice(neighbors)
        connectors = graph.connectors(node, neighbor)
        connector = random.choice(connectors)
        tree.connect(node, neighbor, connector)
        stack.append(neighbor)
        if tree.degree(node) >= node.degree:
          node = neighbor
      elif tree.degree(node) < node.degree and node.degree != graph.order():
        return False
      else:
        if node in stack:
          stack.remove(node)
        node = stack[-1] if stack else None
    return True

  def span_bfs(floor, start=None):
    graph = floor.graph
    tree = floor.tree
    if start is None:
      start = random.choice(graph.nodes)
    node = start
    queue = [node]
    while queue:
      node = queue.pop()
      tree.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n in neighbors if tree.degree(n) == 0]
      if not neighbors and tree.degree(node) < node.degree:
        return False
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
    for node in graph.nodes:
      if node not in tree.nodes:
        for cell in node.get_cells():
          stage.set_tile_at(cell, stage.WALL)
        graph.remove(node)

def debug_floor(seed=None):
  floor = Floor((21, 21))
  if seed is None:
    seed = random.getrandbits(32)
  random.seed(seed)
  floor.stage.seed = seed

  arena = BattleRoom()
  exit_room = floor.gen_room()
  features = [arena, exit_room]
  floor.gen_place(arena)
  floor.tree.add(exit_room)
  if not floor.gen_neighbor(arena, exit_room):
    print("fatal: Failed to place exit room")
    return debug_floor()
  floor.stage.set_tile_at(exit_room.get_center(), Stage.STAIRS_UP)

  rooms = floor.gen_rooms()
  floor.gen_mazes()
  floor.connect()
  if not floor.span_bfs(start=arena):
    print("fatal: Failed to satisfy feature degree constraints")
    return debug_floor()
  floor.fill_ends()
  floor.fill_isolated()

  for (n1, n2), doors in floor.tree.conns.items():
    if isinstance(n1, RectRoom):
      target = n1
    elif isinstance(n2, RectRoom):
      target = n2
    else:
      target = None
    for door in doors:
      floor.draw_door(door, target)

  floor.stage.rooms = rooms + features
  floor.stage.entrance = random.choice(rooms).get_center()
  return floor.stage

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

def dungeon(size, seed=None):
  width, height = size
  stage = Stage((width, height))
  stage.fill(Stage.WALL)

  mazes = gen_mazes(slots)

  node_conns = {}
  conn_nodes = {}
  nodes = rooms + mazes + features
  for node in nodes:
    node_conns[node] = []

  if exit_room and exit_room in nodes:
    nodes.remove(exit_room)

  # connect nodes
  start = random.choice([r for r in rooms if r is not entry_room and r is not exit_room])
  nodes.remove(start)
  stack = [start]
  node = start
  neighbor_table = {}
  loops = []
  while node:
    if node in neighbor_table:
      neighbor_conns = neighbor_table[node]
    else:
      neighbor_conns = get_neighbors(nodes, node)
    # only connect to neighbors that this neighbor hasn't connected to before
    prospects = []
    prospect_loops = []
    neighbors_deg1 = [n1 for n1, _ in node_conns[node]]
    for n1 in neighbor_conns.keys():
      neighbors_deg2 = [n2 for n2, _ in node_conns[n1]]
      if node in neighbors_deg2:
        continue
      looping = node in neighbor_table and n1 in neighbor_table
      if (not [n2 for n2 in neighbors_deg2 if n2 in neighbors_deg1]
      and (len(loops) < config.MAX_LOOPS or not looping)):
        prospects.append(n1)
        if looping:
          prospect_loops.append(n1)
    neighbor_table[node] = neighbor_conns
    if prospects:
      # pick a random neighbor
      neighbor = random.choice(prospects)

      # pick a random connector
      conn = random.choice(neighbor_conns[neighbor])

      # mark connector as door
      doors.append(conn)

      # register the connector as a loop, if applicable
      if neighbor in prospect_loops:
        loops.append(conn)

      # connect this node to that neighbor
      node_conns[node].append((neighbor, conn))
      node_conns[neighbor].append((node, conn))
      conn_nodes[conn] = (node, neighbor)

      # only add neighbor to the stack if it's not visited
      if neighbor in nodes:
        stack.append(neighbor)

      # declare neighbor as visited
      if neighbor in nodes:
        nodes.remove(neighbor)

      # use neighbor for next iteration
      if neighbor not in features:
        node = neighbor
    else:
      if node in stack:
        stack.remove(node)
      node = stack[-1] if stack else None

  if len(node_conns) == 0:
    print("restart: No connections made")
    return dungeon(size)

  for node in nodes:
    if node in features:
      print("restart: Unconnected feature")
      return dungeon(size)

  # remove dead ends
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
  for maze in mazes:
    if len(maze.cells) == 0:
      mazes.remove(maze)

  # root out generations with extremely long corridors
  for maze in mazes:
    score = len(maze.cells) / (len(node_conns[maze]) or 1)
    # print(len(maze.cells), score)
    if len(maze.cells) / (len(node_conns[maze]) or 1) >= 16:
      print("restart: Corridor too long")
      return dungeon(size)

  room_borders = []
  for room in rooms + features:
    room_borders.extend(room.get_border())

  maze_cells = []
  for maze in mazes:
    maze_cells.extend(maze.get_cells())

  # carve out rooms and mazes
  for node in rooms + mazes:
    for cell in node.get_cells():
      stage.set_tile_at(cell, Stage.FLOOR)

  mini_rooms = []
  choices = maze_cells.copy()
  while choices:
    maze_cell = random.choice(choices)
    choices.remove(maze_cell)

    major_axis = random.randint(3, 6)
    if random.randint(1, 2) == 1:
      room_size = (2, major_axis)
    else:
      room_size = (major_axis, 2)

    room_width, room_height = room_size
    cell_x, cell_y = maze_cell
    if random.randint(1, 2) == 1:
      cell_x -= room_width - 1
    if random.randint(1, 2) == 1:
      cell_y -= room_height - 1

    mini_room = Room(room_size, maze_cell)
    for cell in mini_room.get_cells() + mini_room.get_border():
      if (cell in room_borders
      or cell not in maze_cells and stage.get_tile_at(cell) is not Stage.WALL):
        break
    else:
      mini_rooms.append(mini_room)
      for cell in mini_room.get_cells():
        stage.set_tile_at(cell, Stage.FLOOR)

  # draw doors
  secret_rooms = []
  dead_ends = []
  for door in doors:
    x, y = door
    left_tile = stage.get_tile_at((x - 1, y))
    right_tile = stage.get_tile_at((x + 1, y))
    door_tile = Stage.DOOR
    door_inverse = False
    n1, n2 = conn_nodes[door]
    if door in loops and n1 in rooms and n2 in rooms:
      door_tile = random.choice((Stage.DOOR, Stage.FLOOR))
    else:
      for room in rooms + features:
        if room is entry_room or room is exit_room or len(node_conns[room]) != 1:
          continue
        conn_node, conn_door = node_conns[room][0]
        if conn_door != door:
          continue
        can_connect = True
        if conn_node in mazes:
          ends = conn_node.get_ends()
          for end in ends:
            if manhattan(end, conn_door) <= 2:
              can_connect = False
              break
        if floor != 1 and can_connect:
          if not room in features:
            secret_rooms.append(room)
          door_tile = Stage.DOOR_HIDDEN
        elif not room in features:
          dead_ends.append(room)
        if left_tile is Stage.WALL and right_tile is Stage.WALL and conn_node in rooms:
          _, center_y = conn_node.get_center()
          if center_y < y:
            door_inverse = True
        break
    if door_inverse:
      stage.set_tile_at(door, Stage.DOOR_WAY)
      stage.set_tile_at((x, y - 1), door_tile)
    else:
      stage.set_tile_at(door, door_tile)
      if left_tile is Stage.WALL and right_tile is Stage.WALL:
        stage.set_tile_at((x, y - 1), Stage.DOOR_WAY)
  print(loops)

  if len(rooms) == 1:
    print("restart: Too few rooms")
    return dungeon(size)

  normal_rooms = [r for r in rooms if r not in secret_rooms and r not in dead_ends]
  if len(normal_rooms) < 2:
    print("restart: Too few rooms")
    return dungeon(size)

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

  mini_room_cells = []
  for mini_room in mini_rooms:
    mini_room_cells.extend(mini_room.get_cells())

  wanderers = len(mini_room_cells) // 8
  # print(len(mini_room_cells), wanderers)
  while wanderers and len(mini_room_cells):
    cell = random.choice(mini_room_cells)
    mini_room_cells.remove(cell)
    enemy = gen_enemy(floor)
    stage.spawn_elem(enemy, cell)
    wanderers -= 1

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
