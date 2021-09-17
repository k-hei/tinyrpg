from copy import deepcopy
from random import randint, choice
from lib.cell import neighborhood
from dungeon.props.pillar import Pillar

def gen_terrain(stage, room, tree=None):
  # carve out all cells in room except for one cell
  room_cells = room.get_cells()
  for cell in room_cells:
    stage.set_tile_at(cell, stage.PIT)

  # paint floors from each doorway to pivot
  room_doorways = [next((n for n in neighborhood(d) if n in room_cells), None) for d in room.get_doorways(stage)]
  room_doorways = [d for d in room_doorways if d]
  room_pathcells = []

  def create_platform(cell=None):
    pivot = cell or choice(room_cells)
    diagonals = randint(0, 1)
    radius = randint(1, 2) if diagonals else 2
    pivot_neighbors = neighborhood(pivot, radius=radius, diagonals=diagonals, inclusive=True)
    for cell in pivot_neighbors:
      if cell in room_cells:
        stage.set_tile_at(cell, stage.FLOOR)
      if diagonals and radius == 2 and (
        cell in neighborhood(pivot, diagonals=True)
        and cell not in neighborhood(pivot, inclusive=True)
        and not next((n for n in neighborhood(cell, diagonals=True) if (
          n not in room_cells
          or not stage.is_cell_empty(n)
        )), None)
      ):
        stage.spawn_elem_at(cell, Pillar(broken=randint(1, 3) == 1))
    return pivot

  def draw_path(start, goal):
    path = stage.pathfind(start=door, goal=pivot, whitelist=room_cells)
    for cell in path:
      stage.set_tile_at(cell, stage.FLOOR)
      neighbors = [n for n in neighborhood(cell) if n in room_cells]
      if neighbors:
        stage.set_tile_at(choice(neighbors), stage.FLOOR)
    return path

  def find_connected_room(room, door):
    neighbor = next((n for n in tree.neighbors(room) for d in tree.connectors(room, n) if d == door), None)
    return neighbor

  disconnected = False
  pivot = create_platform()
  for door in room_doorways:
    create_platform(cell=door)
    if len(room.get_doorways(stage)) > 1 and room.get_area() > 7 * 4 and room_pathcells and randint(0, 1):
      doorway = next((d for d in room.get_doorways(stage) if d in neighborhood(door)), None)
      neighbor = find_connected_room(room, doorway)
      subtree = tree.copy()
      subtree.remove(room)
      other_neighbor = next((n for n in tree.neighbors(room) if n is not neighbor), None)
      if subtree.path(start=neighbor, goal=other_neighbor):
        tree.disconnect(room, neighbor)
        tree.disconnect(room, other_neighbor)
        print(f"Disconnect {room.origin}")
        disconnected = True
        continue
    room_pathcells += draw_path(start=door, goal=pivot)

  if room_pathcells and room.get_area() > 7 * 4 and not disconnected:
    for i in range(randint(1, 3)):
      pivot = create_platform()
      room_pathcells += draw_path(start=choice(room_pathcells), goal=pivot)

  return True
