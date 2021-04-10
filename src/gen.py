import random
from stage import Stage
from actor import Actor

lengths = (3, 5, 7)

class Room:
  def __init__(room, size, cell=None):
    room.size = size
    room.cell = cell

  def get_cells(room):
    cells = []
    (room_width, room_height) = room.size
    (room_x, room_y) = room.cell
    for y in range(room_height):
      for x in range(room_width):
        cells.append((x + room_x, y + room_y))
    return cells

  def get_center(room):
    (room_width, room_height) = room.size
    (room_x, room_y) = room.cell
    return (room_x + room_width // 2, room_y + room_height // 2)

def cells(size):
  cells = []
  (width, height) = size
  for y in range(height):
    for x in range(width):
      cells.append((x, y))
  return cells

def is_odd(cell):
  return cell[0] % 2 == 1 and cell[1] % 2 == 1

def add(a, b):
  return (a[0] + b[0], a[1] + b[1])

def manhattan(a, b):
  return abs(b[0] - a[0]) + abs(b[1] - a[1])

def dungeon(width, height):
  stage = Stage((width, height))
  stage.fill(Stage.WALL)
  nodes = [cell for cell in stage.get_cells() if is_odd(cell)]

  rooms = gen_rooms(nodes)
  for room in rooms:
    for cell in room.get_cells():
      stage.set_at(cell, Stage.FLOOR)

  room = rooms[0]
  center = room.get_center()
  stage.spawn(Actor("hero", center))
  stage.spawn(Actor("mage", (center[0] - 1, center[1])))

  mazes = gen_mazes(nodes)
  for maze in mazes:
    for cell in maze:
      stage.set_at(cell, Stage.FLOOR)

  room = rooms[1]
  center = room.get_center()
  stage.set_at(center, Stage.STAIRS)

  return stage

def gen_rooms(nodes):
  rooms = []
  valid_nodes = None
  while valid_nodes is None or len(valid_nodes) > 0:
    room_width = random.choice(lengths)
    room_height = random.choice(lengths)
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
    maze = [node]
    stack = [node]
    while node:
      (x, y) = node
      neighbors = [other for other in nodes if manhattan(node, other) == 2]
      if len(neighbors):
        neighbor = random.choice(neighbors)
        (neighbor_x, neighbor_y) = neighbor
        midpoint = ((x + neighbor_x) // 2, (y + neighbor_y) // 2)
        maze.append(midpoint)
        maze.append(neighbor)
        stack.append(neighbor)
        nodes.remove(neighbor)
        node = neighbor
      elif len(stack) > 1:
        stack.pop()
        node = stack[len(stack) - 1]
      else:
        node = None
    mazes.append(maze)
  return mazes
