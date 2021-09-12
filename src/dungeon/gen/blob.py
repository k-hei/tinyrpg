from math import inf, ceil
from random import randint, choice
from lib.cell import neighborhood, add as add_vector
from dungeon.stage import Stage

MIN_ROOM_AREA = 120
MAX_ROOM_AREA = 200
SEED_WALL_RATIO = 0.3
BIRTH_THRESHOLD = 4
DEATH_THRESHOLD = 3
NUM_OF_GENERATIONS = 5

def gen_size():
  room_width = 7 + 2 * randint(0, 10)
  min_height = MIN_ROOM_AREA / room_width
  max_height = MAX_ROOM_AREA / room_width
  room_height = 1 + 3 * randint(ceil((min_height - 1) / 3), (max_height - 1) // 3)
  return (room_width, room_height)

def gen_blob(size=None):
  size = size or gen_size()
  sandbox = Stage(size)
  valid_cells = sandbox.get_cells()
  wall_count = int(len(valid_cells) * SEED_WALL_RATIO)
  while wall_count:
    cell = choice(valid_cells)
    valid_cells.remove(cell)
    sandbox.set_tile_at(cell, Stage.WALL)
    wall_count -= 1

  for i in range(NUM_OF_GENERATIONS):
    sandbox = life(sandbox, birth_threshold=BIRTH_THRESHOLD, death_threshold=DEATH_THRESHOLD)

  islands = find_islands(sandbox)
  if not islands:
    return None

  for island in islands[1:]:
    for cell in island:
      sandbox.set_tile_at(cell, Stage.STAIRS_UP)

  left, top, right, bottom = find_bounds(islands[0])
  sandbox.set_tile_at((left, top), Stage.STAIRS_UP)
  sandbox.set_tile_at((right, top), Stage.STAIRS_UP)
  sandbox.set_tile_at((left, bottom), Stage.STAIRS_UP)
  sandbox.set_tile_at((right, bottom), Stage.STAIRS_UP)

  width = right - left + 1
  height = bottom - top + 1
  stage = Stage((width + 2, height + 2))
  stage.fill(stage.WALL)
  for cell in stage.get_cells():
    offset = add_vector(cell, (left, top))
    tile = sandbox.get_tile_at(offset)
    if tile:
      stage.set_tile_at(add_vector(cell, (1, 1)), tile)

  return stage

def life(stage, birth_threshold, death_threshold):
  stage_copy = Stage(size=stage.size, data=stage.data)
  for cell in stage_copy.get_cells():
    neighbors = neighborhood(cell, diagonals=True)
    walls = len([n for n in neighbors if stage.get_tile_at(n) is stage.WALL or stage.get_tile_at(n) is None])
    if stage.get_tile_at(cell) is stage.WALL:
      stage_copy.set_tile_at(cell, stage.FLOOR if walls < death_threshold else stage.WALL)
    else:
      stage_copy.set_tile_at(cell, stage.WALL if walls > birth_threshold else stage.FLOOR)
  return stage_copy

def flood_fill(stage, cell):
  island = [cell]
  stack = [cell]
  while stack:
    cell = stack.pop()
    for neighbor in neighborhood(cell):
      if stage.get_tile_at(neighbor) is stage.FLOOR and neighbor not in island:
        island.append(neighbor)
        stack.append(neighbor)
  return island

def find_islands(stage):
  islands = []
  island_cells = []
  for cell in stage.get_cells():
    if stage.get_tile_at(cell) is stage.FLOOR and cell not in island_cells:
      island = flood_fill(stage, cell)
      islands.append(island)
      island_cells += island
  return islands

def find_bounds(cells):
  left = inf
  top = inf
  right = -inf
  bottom = -inf
  for (x, y) in cells:
    if x < left:
      left = x
    elif x > right:
      right = x
    if y < top:
      top = y
    elif y > bottom:
      bottom = y
  return (left, top, right, bottom)
