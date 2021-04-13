import random
from cell import is_odd, add, is_adjacent, manhattan
from stage import Stage
from room import Room
from maze import Maze

from actors import Knight, Mage, Eye, Chest
from actors.mimic import Mimic

from items.potion import Potion
from items.ankh import Ankh
from items.cheese import Cheese
from items.bread import Bread
from items.fish import Fish
from items.emerald import Emerald

possible_widths = (3, 5, 7)
possible_heights = (3, 5, 7)

def cells(size):
  cells = []
  (width, height) = size
  for y in range(height):
    for x in range(width):
      cells.append((x, y))
  return cells

def get_neighbors(nodes, node):
  neighbors = {}
  for edge in node.get_edges():
    (x, y) = edge
    adj_cells = [
      (x - 1, y),
      (x, y - 1),
      (x + 1, y),
      (x, y + 1)
    ]
    for cell in adj_cells:
      neighbor = next((target for target in nodes if target is not node and cell in target.get_cells()), None)
      if neighbor:
        if neighbor in neighbors:
          neighbors[neighbor].append(edge)
        else:
          neighbors[neighbor] = [edge]
  return neighbors

def dungeon(size, floor=1):
  width, height = size
  stage = Stage((width, height))
  stage.fill(Stage.WALL)
  slots = [cell for cell in stage.get_cells() if is_odd(cell)]

  entry_room = None
  exit_room = None
  doors = []
  if floor == 1:
    entry_room = Room((5, 7), (width // 2 - 2, height - 8))
    exit_room = Room((5, 3), (width // 2 - 2, height - 8 - 4))
    doors.append((width // 2, height - 9))
    cells = entry_room.get_cells() + exit_room.get_cells()
    for cell in cells:
      if cell in slots:
        slots.remove(cell)

  rooms = gen_rooms(slots)
  if len(rooms) == 1:
    return dungeon(size, floor)

  if entry_room:
    rooms.insert(0, entry_room)
    rooms.insert(1, exit_room)

  conns = {}
  mazes = gen_mazes(slots)
  nodes = rooms + mazes
  for node in nodes:
    conns[node] = []

  if exit_room:
    nodes.remove(exit_room)

  node = random.choice(nodes)
  nodes.remove(node)
  stack = [node]
  while node:
    neighbors = get_neighbors(nodes, node)
    targets = [neighbor for neighbor in list(neighbors.keys()) if next((target for target, conn in conns[node] if target is neighbor), None) is None]
    if len(targets) > 0:
      # pick a random neighbor
      neighbor = random.choice(targets)

      # pick a random connector
      conn = random.choice(neighbors[neighbor])

      # mark connector as door
      doors.append(conn)

      # connect this node to that neighbor
      conns[node].append((neighbor, conn))
      conns[neighbor].append((node, conn))

      # only add neighbor to the stack if it's not visited (allows loops)
      if neighbor in nodes:
        stack.append(neighbor)

      # declare neighbor as visited
      if random.randint(1, 5) != 1:
        nodes.remove(neighbor)

      # use neighbor for next iteration
      node = neighbor
    else:
      stack.remove(node)
      if len(stack) > 0:
        node = stack[len(stack) - 1]
      else:
        node = None

  for maze in mazes:
    if len(conns[maze]) == 1:
      (neighbor, conn) = conns[maze][0]
      doors.remove(conn)
    stack = maze.get_ends()
    while len(stack) > 0:
      end = stack.pop()
      door = next((door for door in doors if is_adjacent(door, end)), None)
      if door is None:
        neighbors = [cell for cell in maze.cells if is_adjacent(cell, end)]
        if len(neighbors) <= 1 and end in maze.cells:
          maze.cells.remove(end)
        if len(neighbors) == 1:
          stack.append(neighbors[0])
    if len(mazes) == 0:
      mazes.remove(maze)

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
    for room in rooms:
      if room is entry_room or room is exit_room:
        continue
      if len(conns[room]) == 1:
        _, conn_door = conns[room][0]
        if conn_door == door:
          if random.randint(1, 5) == 1 and floor != 1:
            secret_rooms.append(room)
            stage.set_tile_at(door, Stage.DOOR_HIDDEN)
          else:
            dead_ends.append(room)
            stage.set_tile_at(door, Stage.DOOR)
          break
    else:
      stage.set_tile_at(door, Stage.DOOR)

  if len(rooms) == 1:
    return dungeon(size, floor)

  normal_rooms = [r for r in rooms if r not in secret_rooms and r not in dead_ends]
  if len(normal_rooms) < 2:
    return dungeon(size, floor)

  if entry_room is None:
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
    stage.set_tile_at(entry_room.get_center(), Stage.STAIRS_DOWN)
    normal_rooms.remove(entry_room)
  else:
    center_x, _ = entry_room.get_center()
    stage.set_tile_at((center_x, height - 1), Stage.DOOR_LOCKED)
    if entry_room in normal_rooms:
      normal_rooms.remove(entry_room)

  if exit_room is None:
    exit_room = random.choice(normal_rooms)

  stage.set_tile_at(exit_room.get_center(), Stage.STAIRS_UP)
  if exit_room in normal_rooms:
    normal_rooms.remove(exit_room)

  for room in normal_rooms:
    for cell in room.get_cells():
      is_floor = stage.get_tile_at(cell) is Stage.FLOOR
      is_empty = stage.get_actor_at(cell) is None
      is_beside_door = next((door for door in doors if is_adjacent(door, cell)), None)
      if not is_floor or not is_empty or is_beside_door:
        continue
      if random.randint(1, 25) == 1:
        enemy = Eye()
        stage.spawn_actor(enemy, cell)
        if random.randint(1, 3) == 1:
          enemy.asleep = True
      elif random.randint(1, 80) == 1:
        item = gen_item()
        stage.spawn_actor(Chest(item), cell)

  for room in dead_ends:
    room_width, room_height = room.size
    max_elems = min(room_width, room_height)
    elems = random.randint(1, max_elems)
    cells = [c for c in room.get_cells() if next((d for d in doors if is_adjacent(d, c)), None) is None]
    for i in range(elems):
      cell = random.choice(cells)
      cells.remove(cell)
      kind = random.choices(("Item", "Mimic", "Eye"), (2, 1, 2))[0]
      if kind == "Item":
        item = gen_item()
        stage.spawn_actor(Chest(item), cell)
      elif kind == "Eye":
        enemy = Eye()
        stage.spawn_actor(enemy, cell)
        if random.randint(1, 3) == 1:
          enemy.asleep = True
      elif kind == "Mimic":
        enemy = Mimic()
        stage.spawn_actor(enemy, cell)

  for room in secret_rooms:
    kind = random.choice(("Treasure", "MonsterDen"))
    for cell in room.get_cells():
      is_floor = stage.get_tile_at(cell) is Stage.FLOOR
      is_empty = stage.get_actor_at(cell) is None
      is_beside_door = next((door for door in doors if is_adjacent(door, cell)), None)
      if not is_floor or not is_empty or is_beside_door:
        continue
      if kind == "Treasure" and random.randint(1, 2) == 1:
        if random.randint(1, 5) == 1:
          enemy = Mimic()
          stage.spawn_actor(enemy, cell)
        else:
          item = random.choice((Potion, Ankh, Bread, Fish, Emerald))()
          stage.spawn_actor(Chest(item), cell)
      elif kind == "MonsterDen" and random.randint(1, 2) == 1:
        enemy = Eye()
        if random.randint(0, 4):
          enemy.asleep = True
        stage.spawn_actor(enemy, cell)

  stage.rooms = rooms
  return stage

def gen_item():
   return random.choices((Potion, Ankh, Cheese, Bread, Fish, Emerald), (3, 1, 4, 3, 1, 1))[0]()

def gen_rooms(slots):
  rooms = []
  valid_slots = None
  while valid_slots is None or len(valid_slots) > 0:
    room_width = random.choice(possible_widths)
    room_height = random.choice(possible_heights)
    valid_slots = []
    for slot in slots:
      offset_cells = map(lambda cell: add(cell, slot), cells((room_width, room_height)))
      odd_offset_cells = [cell for cell in offset_cells if is_odd(cell)]
      cell_has_slot = map(lambda cell: len([slot for slot in slots if slot == cell]) == 1, odd_offset_cells)
      if all(cell_has_slot):
        valid_slots.append(slot)
    if len(valid_slots) > 0:
      slot = random.choice(valid_slots)
      room = Room((room_width, room_height), slot)
      rooms.append(room)
      for cell in map(lambda cell: add(cell, room.cell), cells(room.size)):
        slot = next((slot for slot in slots if slot == cell), None)
        if slot:
          slots.remove(slot)
  return rooms

def gen_mazes(slots):
  mazes = []
  while len(slots) > 0:
    slot = random.choice(slots)
    slots.remove(slot)
    cells = [slot]
    stack = [slot]
    while slot:
      (x, y) = slot
      neighbors = [other for other in slots if manhattan(slot, other) == 2]
      if len(neighbors):
        neighbor = random.choice(neighbors)
        (neighbor_x, neighbor_y) = neighbor
        midpoint = ((x + neighbor_x) // 2, (y + neighbor_y) // 2)
        cells.append(midpoint)
        cells.append(neighbor)
        stack.append(neighbor)
        slots.remove(neighbor)
        slot = neighbor
      elif len(stack) > 1:
        stack.pop()
        slot = stack[len(stack) - 1]
      else:
        slot = None
    mazes.append(Maze(cells))
  return mazes
