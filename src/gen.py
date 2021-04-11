import random
from cell import is_odd, add, is_adjacent, manhattan
from stage import Stage
from room import Room
from maze import Maze
from actors import Knight, Mage, Eye, Chest

possible_widths = (3, 5, 7)
possible_heights = [3]

def cells(size):
  cells = []
  (width, height) = size
  for y in range(height):
    for x in range(width):
      cells.append((x, y))
  return cells

def get_neighbors(elems, elem):
  neighbors = {}
  for edge in elem.get_edges():
    (x, y) = edge
    adj_cells = [
      (x - 1, y),
      (x, y - 1),
      (x + 1, y),
      (x, y + 1)
    ]
    for cell in adj_cells:
      neighbor = next((target for target in elems if target is not elem and cell in target.get_cells()), None)
      if neighbor:
        if neighbor in neighbors:
          neighbors[neighbor].append(edge)
        else:
          neighbors[neighbor] = [edge]
  return neighbors

def dungeon(width, height, players):
  stage = Stage((width, height))
  stage.fill(Stage.WALL)
  nodes = [cell for cell in stage.get_cells() if is_odd(cell)]

  rooms = gen_rooms(nodes)
  if len(rooms) == 1:
    return dungeon(width, height)

  mazes = gen_mazes(nodes)

  doors = []
  conns = {}
  elems = rooms + mazes
  for elem in elems:
    conns[elem] = []

  elem = random.choice(elems)
  elems.remove(elem)
  stack = [elem]
  while elem:
    neighbors = get_neighbors(elems, elem)
    targets = [neighbor for neighbor in list(neighbors.keys()) if next((target for target, conn in conns[elem] if target is neighbor), None) is None]
    if len(targets) > 0:
      # pick a random neighbor
      neighbor = random.choice(targets)

      # pick a random connector
      conn = random.choice(neighbors[neighbor])

      # mark connector as door
      doors.append(conn)

      # connect this elem to that neighbor
      conns[elem].append((neighbor, conn))
      conns[neighbor].append((elem, conn))

      # only add neighbor to the stack if it's not visited (allows loops)
      if neighbor in elems:
        stack.append(neighbor)

      # declare neighbor as visited
      if random.randint(1, 5) != 1:
        elems.remove(neighbor)

      # use neighbor for next iteration
      elem = neighbor
    else:
      stack.remove(elem)
      if len(stack) > 0:
        elem = stack[len(stack) - 1]
      else:
        elem = None

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

  for elem in rooms + mazes:
    for cell in elem.get_cells():
      stage.set_tile_at(cell, Stage.FLOOR)

  for door in doors:
    for room in rooms:
      if len(conns[room]) == 1:
        _, conn_door = conns[room][0]
        if conn_door == door:
          if random.randint(1, 5) == 1:
            stage.set_tile_at(door, Stage.DOOR_HIDDEN)
          else:
            stage.set_tile_at(door, Stage.DOOR)
          break
    else:
      stage.set_tile_at(door, Stage.DOOR)

  room = rooms[0]
  center_x, center_y = room.get_center()
  if players:
    p1, p2 = players
  else:
    p1 = Knight()
    p2 = Mage()

  if not p1.dead:
    stage.spawn(p1, (center_x, center_y))

  if not p2.dead:
    stage.spawn(p2, (center_x - 1, center_y))

  room = rooms[1]
  center = room.get_center()
  stage.set_tile_at(center, Stage.STAIRS)

  for room in rooms:
    for cell in room.get_cells():
      is_floor = stage.get_tile_at(cell) is Stage.FLOOR
      is_empty = stage.get_actor_at(cell) is None
      is_beside_door = next((door for door in doors if is_adjacent(door, cell)), None)
      if not is_floor or not is_empty or is_beside_door:
        continue
      if random.randint(1, 30) == 1:
        enemy = Eye()
        stage.spawn(enemy, cell)
        if random.randint(1, 3) == 1:
          enemy.asleep = True
      elif random.randint(1, 80) == 1:
        choice = random.randint(1, 10)
        if choice == 1:
          stage.spawn(Chest("Warp Crystal"), cell)
        elif choice <= 4:
          stage.spawn(Chest("Bread"), cell)
        else:
          stage.spawn(Chest("Potion"), cell)

  stage.rooms = rooms
  return stage

def gen_rooms(nodes):
  rooms = []
  valid_nodes = None
  while valid_nodes is None or len(valid_nodes) > 0:
    room_width = random.choice(possible_widths)
    room_height = random.choice(possible_heights)
    valid_nodes = []
    for node in nodes:
      offset_cells = map(lambda cell: add(cell, node), cells((room_width, room_height)))
      odd_offset_cells = [cell for cell in offset_cells if is_odd(cell)]
      cell_has_node = map(lambda cell: len([node for node in nodes if node == cell]) == 1, odd_offset_cells)
      if all(cell_has_node):
        valid_nodes.append(node)
    if len(valid_nodes) > 0:
      node = random.choice(valid_nodes)
      room = Room((room_width, room_height), node)
      rooms.append(room)
      for cell in map(lambda cell: add(cell, room.cell), cells(room.size)):
        node = next((node for node in nodes if node == cell), None)
        if node:
          nodes.remove(node)
  return rooms

def gen_mazes(nodes):
  mazes = []
  while len(nodes) > 0:
    node = random.choice(nodes)
    nodes.remove(node)
    cells = [node]
    stack = [node]
    while node:
      (x, y) = node
      neighbors = [other for other in nodes if manhattan(node, other) == 2]
      if len(neighbors):
        neighbor = random.choice(neighbors)
        (neighbor_x, neighbor_y) = neighbor
        midpoint = ((x + neighbor_x) // 2, (y + neighbor_y) // 2)
        cells.append(midpoint)
        cells.append(neighbor)
        stack.append(neighbor)
        nodes.remove(neighbor)
        node = neighbor
      elif len(stack) > 1:
        stack.pop()
        node = stack[len(stack) - 1]
      else:
        node = None
    mazes.append(Maze(cells))
  return mazes
