import random
from grid import Grid

lengths = (3, 5, 7)

class Room:
  def __init__(room, size, cell=None):
    room.size = size
    room.cell = cell

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

def equals(a, b):
  return a[0] == b[0] and a[1] == b[1]

def manhattan(a, b):
  return abs(b[0] - a[0]) + abs(b[1] - a[1])

def default():
  grid = Grid((11, 11))
  grid.data = [
    1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1,
  ]

def maze(width, height):
  grid = Grid((width, height))
  grid.fill(1)
  nodes = [cell for cell in grid.get_cells() if is_odd(cell)]

  rooms = []
  valid_nodes = None
  while valid_nodes is None or len(valid_nodes) > 0:
    room_width = random.choice(lengths)
    room_height = random.choice(lengths)
    valid_nodes = []
    for node in nodes:
      offset_cells = map(lambda cell: add(cell, node), cells((room_width, room_height)))
      odd_offset_cells = [cell for cell in offset_cells if is_odd(cell)]
      cell_has_node = map(lambda cell: len([node for node in nodes if equals(node, cell)]) == 1, odd_offset_cells)
      if all(cell_has_node):
        valid_nodes.append(node)

    if len(valid_nodes) > 0:
      node = random.choice(valid_nodes)
      room = Room((room_width, room_height), node)
      rooms.append(room)
      for cell in map(lambda cell: add(cell, room.cell), cells(room.size)):
        grid.set_at(cell, 0)
        node = next((node for node in nodes if equals(node, cell)), None)
        if node:
          nodes.remove(node)

  nodes = [cell for cell in grid.get_cells() if is_odd(cell)]
  start = random.choice(nodes)
  nodes.remove(start)
  node = start
  stack = [start]
  while node:
    grid.set_at(node, 0)
    (x, y) = node
    neighbors = [other for other in nodes if manhattan(node, other) == 2]
    if len(neighbors):
      neighbor = random.choice(neighbors)
      (neighbor_x, neighbor_y) = neighbor
      midpoint = ((x + neighbor_x) // 2, (y + neighbor_y) // 2)
      grid.set_at(midpoint, 0)
      stack.append(neighbor)
      nodes.remove(neighbor)
      node = neighbor
    elif len(stack) > 1:
      stack.pop()
      node = stack[len(stack) - 1]
    else:
      node = None
  return grid
