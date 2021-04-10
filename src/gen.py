import random
from stage import Stage
from actor import Actor
from room import Room

lengths = (3, 5, 7)

class Maze:
  def __init__(maze, cells):
    maze.cells = cells

  def get_cells(maze):
    return maze.cells

  def get_edges(maze):
    edges = []
    for cell in maze.cells:
      (x, y) = cell
      adj_cells = [
        (x - 1, y),
        (x, y - 1),
        (x + 1, y),
        (x, y + 1)
      ]
      for adj in adj_cells:
        if not adj in edges:
          edges.append(adj)
    return edges

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

def dungeon(width, height):
  stage = Stage((width, height))
  stage.fill(Stage.WALL)
  nodes = [cell for cell in stage.get_cells() if is_odd(cell)]

  rooms = gen_rooms(nodes)
  for room in rooms:
    for cell in room.get_cells():
      stage.set_at(cell, Stage.FLOOR)

  mazes = gen_mazes(nodes)
  for maze in mazes:
    for cell in maze.get_cells():
      stage.set_at(cell, Stage.FLOOR)

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
    if len(neighbors) > 0:
      # pick a random neighbor
      neighbor = random.choice(list(neighbors.keys()))

      # pick a random connector
      conn = random.choice(neighbors[neighbor])

      # mark connector as door
      doors.append(conn)

      # connect this elem to that neighbor
      conns[elem].append(neighbor)
      conns[neighbor].append(elem)

      # only add neighbor to the stack if it's not visited (allows loops)
      if neighbor in elems:
        stack.append(neighbor)

      # declare neighbor as visited
      elems.remove(neighbor)

      # use neighbor for next iteration
      elem = neighbor
    else:
      stack.remove(elem)
      # remove maze if it's a dead end
      if len(stack) > 0:
        elem = stack[len(stack) - 1]
      else:
        elem = None

  for door in doors:
    stage.set_at(door, Stage.FLOOR)

  room = rooms[0]
  center = room.get_center()
  stage.spawn(Actor("hero", center))
  stage.spawn(Actor("mage", (center[0] - 1, center[1])))

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
