from math import inf, ceil
from random import randint, choice
from lib.cell import neighborhood, add as add_vector
from lib.bounds import find_bounds
from dungeon.stage import Stage

MIN_ROOM_AREA = 120
SEED_WALL_RATIO = 0.3
BIRTH_THRESHOLD = 4
DEATH_THRESHOLD = 3
NUM_OF_GENERATIONS = 5

def gen_size(min_area, max_area=None):
  if max_area is None:
    max_area = min_area + 20
  room_width = 7 + 2 * randint(0, 10)
  min_height = min_area / room_width
  max_height = max_area / room_width
  min_factor = ceil((min_height - 1) / 3)
  max_factor = (max_height - 1) // 3
  room_height = 1 + 3 * (randint if max_factor > min_factor else max)(min_factor, max_factor)
  return (room_width, room_height)

def gen_blob(size=None, min_area=MIN_ROOM_AREA, max_area=None):
  while True:
    size = size or gen_size(min_area=min_area, max_area=max_area)
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
      continue

    for island in islands[1:]:
      for cell in island:
        sandbox.set_tile_at(cell, Stage.STAIRS_UP)

    island_rect = find_bounds(islands[0])
    if island_rect.width * island_rect.height < min_area // 3:
      continue

    return [add_vector(c, (-island_rect.left, -island_rect.top)) for c in islands[0]]


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
